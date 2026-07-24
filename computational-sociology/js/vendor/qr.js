// Minimal QR encoder, byte mode, error correction level M, versions 1..10.
// Public domain. Adapted from Project Nayuki's QR-Code-generator (MIT-0)
// with fixed-tables versioned block structure.
//
// Usage:
//   const svg = QR.svg("https://example.com/…", { size: 200, margin: 4 });
//   document.getElementById("host").innerHTML = svg;
//
// Only byte mode (UTF-8). Only error level M (~15% recovery). Auto-picks the
// smallest version that fits the input (up to 216 data bytes = version 10 M).

(function (root) {
  "use strict";

  // ---------- GF(256) tables, primitive polynomial 0x11d ----------
  var EXP = new Uint8Array(256);
  var LOG = new Uint8Array(256);
  (function () {
    var x = 1;
    for (var i = 0; i < 255; i++) {
      EXP[i] = x;
      LOG[x] = i;
      x <<= 1;
      if (x >= 256) x ^= 0x11d;
    }
    EXP[255] = EXP[0];
  })();
  function gfMul(a, b) { return a === 0 || b === 0 ? 0 : EXP[(LOG[a] + LOG[b]) % 255]; }

  // ---------- Reed-Solomon generator polynomial and encoding ----------
  function rsGenerator(degree) {
    // g(x) = (x + a^0)(x + a^1)...(x + a^(deg-1))
    var g = [1];
    for (var i = 0; i < degree; i++) {
      var next = new Array(g.length + 1).fill(0);
      for (var j = 0; j < g.length; j++) {
        next[j] ^= g[j];
        next[j + 1] ^= gfMul(g[j], EXP[i]);
      }
      g = next;
    }
    return g;
  }
  function rsEncode(data, ecLen) {
    var g = rsGenerator(ecLen);
    var buf = new Uint8Array(data.length + ecLen);
    for (var i = 0; i < data.length; i++) buf[i] = data[i];
    for (var i = 0; i < data.length; i++) {
      var f = buf[i];
      if (f === 0) continue;
      for (var j = 0; j <= ecLen; j++) buf[i + j] ^= gfMul(g[j], f);
    }
    return buf.slice(data.length);
  }

  // ---------- Version tables for level M ----------
  // Per version 1..10: total codewords, data codewords, ec per block, block sizes (data).
  // block sizes list is the DATA codewords per block; ec per block is uniform.
  var VER_M = [
    /* v1  */ { total: 26,  data: 16,  ecPerBlock: 10, blocks: [16] },
    /* v2  */ { total: 44,  data: 28,  ecPerBlock: 16, blocks: [28] },
    /* v3  */ { total: 70,  data: 44,  ecPerBlock: 26, blocks: [44] },
    /* v4  */ { total: 100, data: 64,  ecPerBlock: 18, blocks: [32, 32] },
    /* v5  */ { total: 134, data: 86,  ecPerBlock: 24, blocks: [43, 43] },
    /* v6  */ { total: 172, data: 108, ecPerBlock: 16, blocks: [27, 27, 27, 27] },
    /* v7  */ { total: 196, data: 124, ecPerBlock: 18, blocks: [31, 31, 31, 31] },
    /* v8  */ { total: 242, data: 154, ecPerBlock: 22, blocks: [38, 38, 39, 39] },
    /* v9  */ { total: 292, data: 182, ecPerBlock: 22, blocks: [36, 36, 36, 36, 37] },
    /* v10 */ { total: 346, data: 216, ecPerBlock: 26, blocks: [43, 43, 43, 43, 44, 44] }
  ];

  // Alignment pattern positions for versions 2..10. v1 has none.
  var ALIGN = [
    null,             // v1
    [6, 18],          // v2
    [6, 22],          // v3
    [6, 26],          // v4
    [6, 30],          // v5
    [6, 34],          // v6
    [6, 22, 38],      // v7
    [6, 24, 42],      // v8
    [6, 26, 46],      // v9
    [6, 28, 50]       // v10
  ];

  // Format info bits for level M, masks 0..7 (15-bit BCH-encoded values).
  var FORMAT_M = [0x5412, 0x5125, 0x5E7C, 0x5B4B, 0x45F9, 0x40CE, 0x4F97, 0x4AA0];

  // ---------- Text → bytes (UTF-8) ----------
  function utf8Bytes(text) {
    if (typeof TextEncoder !== "undefined") return new TextEncoder().encode(text);
    var out = [];
    for (var i = 0; i < text.length; i++) {
      var c = text.charCodeAt(i);
      if (c < 0x80) out.push(c);
      else if (c < 0x800) { out.push(0xc0 | (c >> 6)); out.push(0x80 | (c & 0x3f)); }
      else { out.push(0xe0 | (c >> 12)); out.push(0x80 | ((c >> 6) & 0x3f)); out.push(0x80 | (c & 0x3f)); }
    }
    return new Uint8Array(out);
  }

  // ---------- Bit buffer ----------
  function BitBuf() { this.bits = []; }
  BitBuf.prototype.push = function (val, n) {
    for (var i = n - 1; i >= 0; i--) this.bits.push((val >> i) & 1);
  };
  BitBuf.prototype.toBytes = function () {
    var b = new Uint8Array(Math.ceil(this.bits.length / 8));
    for (var i = 0; i < this.bits.length; i++) {
      if (this.bits[i]) b[i >> 3] |= 0x80 >> (i & 7);
    }
    return b;
  };

  // ---------- Choose smallest version that fits ----------
  function pickVersion(nBytes) {
    for (var v = 0; v < VER_M.length; v++) {
      // Byte-mode overhead: 4 mode bits + 8 or 16 length bits.
      // For versions 1-9: 8-bit count. Versions 10-40: 16-bit count.
      var countBits = v + 1 <= 9 ? 8 : 16;
      var overheadBits = 4 + countBits;
      var capacityBits = VER_M[v].data * 8;
      if (overheadBits + nBytes * 8 <= capacityBits) return v + 1;
    }
    throw new Error("URL prea lung pentru versiunile 1..10.");
  }

  // ---------- Build data codewords (interleaved) ----------
  function buildDataCodewords(text, ver) {
    var bytes = utf8Bytes(text);
    var info = VER_M[ver - 1];
    var countBits = ver <= 9 ? 8 : 16;
    var bb = new BitBuf();
    bb.push(0x4, 4);              // byte mode
    bb.push(bytes.length, countBits);
    for (var i = 0; i < bytes.length; i++) bb.push(bytes[i], 8);
    // Terminator (up to 4 zero bits), then pad to byte boundary, then pad codewords.
    var capacityBits = info.data * 8;
    var termLen = Math.min(4, capacityBits - bb.bits.length);
    bb.push(0, termLen);
    while (bb.bits.length % 8 !== 0) bb.bits.push(0);
    var dataBytes = bb.toBytes();
    var padded = new Uint8Array(info.data);
    for (var i = 0; i < dataBytes.length; i++) padded[i] = dataBytes[i];
    for (var i = dataBytes.length, tog = 0; i < info.data; i++, tog++) {
      padded[i] = tog % 2 === 0 ? 0xEC : 0x11;
    }

    // Split into blocks per info.blocks, compute EC per block, then interleave.
    var dataBlocks = [];
    var ecBlocks = [];
    var offset = 0;
    for (var b = 0; b < info.blocks.length; b++) {
      var blockLen = info.blocks[b];
      var dataBlock = padded.slice(offset, offset + blockLen);
      offset += blockLen;
      dataBlocks.push(dataBlock);
      ecBlocks.push(rsEncode(dataBlock, info.ecPerBlock));
    }
    // Interleave data column-major, then ec column-major.
    var maxData = Math.max.apply(null, info.blocks);
    var out = [];
    for (var col = 0; col < maxData; col++) {
      for (var b = 0; b < dataBlocks.length; b++) {
        if (col < dataBlocks[b].length) out.push(dataBlocks[b][col]);
      }
    }
    for (var col = 0; col < info.ecPerBlock; col++) {
      for (var b = 0; b < ecBlocks.length; b++) {
        out.push(ecBlocks[b][col]);
      }
    }
    return new Uint8Array(out);
  }

  // ---------- Matrix construction ----------
  function newMatrix(size) {
    var m = new Array(size);
    var reserved = new Array(size);
    for (var y = 0; y < size; y++) {
      m[y] = new Uint8Array(size);
      reserved[y] = new Uint8Array(size);
    }
    return { m: m, res: reserved, size: size };
  }
  function setModule(mat, x, y, v) { mat.m[y][x] = v ? 1 : 0; mat.res[y][x] = 1; }
  function placeFinder(mat, cx, cy) {
    for (var dy = -1; dy <= 7; dy++) {
      for (var dx = -1; dx <= 7; dx++) {
        var x = cx + dx, y = cy + dy;
        if (x < 0 || y < 0 || x >= mat.size || y >= mat.size) continue;
        var dist = Math.max(Math.abs(dx - 3), Math.abs(dy - 3));
        setModule(mat, x, y, dist !== 2 && dist !== 4);
      }
    }
  }
  function placeAlignment(mat, cx, cy) {
    for (var dy = -2; dy <= 2; dy++) {
      for (var dx = -2; dx <= 2; dx++) {
        var dist = Math.max(Math.abs(dx), Math.abs(dy));
        setModule(mat, cx + dx, cy + dy, dist !== 1);
      }
    }
  }
  function placeTiming(mat) {
    for (var i = 8; i < mat.size - 8; i++) {
      setModule(mat, i, 6, i % 2 === 0);
      setModule(mat, 6, i, i % 2 === 0);
    }
  }
  function reserveFormat(mat) {
    // Format info occupies 15 modules in two mirrored regions. Take care
    // NOT to overwrite the two timing modules at (col=6, row=8) and
    // (col=8, row=6), which sit on the border of the reserved area.
    var size = mat.size;
    // Top-left region:
    for (var i = 0; i < 6; i++) setModule(mat, 8, i, 0);       // col 8, rows 0..5
    setModule(mat, 8, 7, 0);                                    // col 8, row 7 (skip row 6)
    setModule(mat, 8, 8, 0);                                    // col 8, row 8
    setModule(mat, 7, 8, 0);                                    // col 7, row 8 (skip col 6)
    for (var i = 0; i < 6; i++) setModule(mat, 5 - i, 8, 0);   // row 8, cols 5..0
    // Redundant copy split between top-right (horizontal) and bottom-left (vertical):
    for (var i = 0; i < 8; i++) setModule(mat, size - 1 - i, 8, 0);
    for (var i = 0; i < 7; i++) setModule(mat, 8, size - 7 + i, 0);
    // Dark module (always 1) at (col=8, row=size-8)
    setModule(mat, 8, size - 8, 1);
  }
  function writeFormat(mat, mask) {
    var bits = FORMAT_M[mask];
    var size = mat.size;
    // Top-left copy (matches reserveFormat layout above).
    // mat.m[row][col]; setting mat.m[y][x].
    for (var i = 0; i < 6; i++) mat.m[i][8] = (bits >> i) & 1;    // col 8, rows 0..5
    mat.m[7][8] = (bits >> 6) & 1;                                 // col 8, row 7
    mat.m[8][8] = (bits >> 7) & 1;                                 // col 8, row 8
    mat.m[8][7] = (bits >> 8) & 1;                                 // col 7, row 8
    for (var i = 9; i < 15; i++) mat.m[8][14 - i] = (bits >> i) & 1; // row 8, cols 5..0
    // Redundant copy: top-right horizontal + bottom-left vertical.
    for (var i = 0; i < 8; i++) mat.m[8][size - 1 - i] = (bits >> i) & 1;
    for (var i = 8; i < 15; i++) mat.m[size - 15 + i][8] = (bits >> i) & 1;
    // Dark module.
    mat.m[size - 8][8] = 1;
  }
  function placeDataBits(mat, codewords) {
    // Walk the matrix in zigzag from bottom-right, skipping reserved cells.
    var bitIdx = 0;
    var totalBits = codewords.length * 8;
    for (var right = mat.size - 1; right >= 1; right -= 2) {
      if (right === 6) right = 5; // skip timing column
      for (var vert = 0; vert < mat.size; vert++) {
        for (var jj = 0; jj < 2; jj++) {
          var x = right - jj;
          var upward = ((right + 1) & 2) === 0;
          var y = upward ? mat.size - 1 - vert : vert;
          if (!mat.res[y][x] && bitIdx < totalBits) {
            var bit = (codewords[bitIdx >> 3] >> (7 - (bitIdx & 7))) & 1;
            mat.m[y][x] = bit;
            bitIdx++;
          }
        }
      }
    }
  }
  function maskFn(mask, x, y) {
    switch (mask) {
      case 0: return (x + y) % 2 === 0;
      case 1: return y % 2 === 0;
      case 2: return x % 3 === 0;
      case 3: return (x + y) % 3 === 0;
      case 4: return (Math.floor(y / 2) + Math.floor(x / 3)) % 2 === 0;
      case 5: return (x * y) % 2 + (x * y) % 3 === 0;
      case 6: return ((x * y) % 2 + (x * y) % 3) % 2 === 0;
      case 7: return ((x + y) % 2 + (x * y) % 3) % 2 === 0;
    }
    return false;
  }
  function applyMask(mat, mask) {
    for (var y = 0; y < mat.size; y++) {
      for (var x = 0; x < mat.size; x++) {
        if (!mat.res[y][x] && maskFn(mask, x, y)) {
          mat.m[y][x] ^= 1;
        }
      }
    }
  }
  function score(mat) {
    var s = 0;
    var size = mat.size;
    // Rule 1: runs of same-color modules in a row/column (5+ = 3 + extra)
    function scoreLine(get) {
      var c = 1, prev = get(0), sum = 0;
      for (var i = 1; i < size; i++) {
        var v = get(i);
        if (v === prev) { c++; }
        else { if (c >= 5) sum += 3 + (c - 5); c = 1; prev = v; }
      }
      if (c >= 5) sum += 3 + (c - 5);
      return sum;
    }
    for (var y = 0; y < size; y++) s += scoreLine(function (x) { return mat.m[y][x]; });
    for (var x = 0; x < size; x++) s += scoreLine(function (y) { return mat.m[y][x]; });
    // Rule 2: 2x2 blocks of same color
    for (var y = 0; y < size - 1; y++) {
      for (var x = 0; x < size - 1; x++) {
        var v = mat.m[y][x];
        if (v === mat.m[y][x + 1] && v === mat.m[y + 1][x] && v === mat.m[y + 1][x + 1]) s += 3;
      }
    }
    // Rule 3: finder-like patterns 1:1:3:1:1 with 4-module quiet on one side
    var pat1 = [1, 0, 1, 1, 1, 0, 1, 0, 0, 0, 0];
    var pat2 = [0, 0, 0, 0, 1, 0, 1, 1, 1, 0, 1];
    function checkPat(pattern, get, start) {
      for (var i = 0; i < pattern.length; i++) if (get(start + i) !== pattern[i]) return false;
      return true;
    }
    for (var y = 0; y < size; y++) {
      for (var x = 0; x <= size - 11; x++) {
        if (checkPat(pat1, function (i) { return mat.m[y][i]; }, x)) s += 40;
        if (checkPat(pat2, function (i) { return mat.m[y][i]; }, x)) s += 40;
      }
    }
    for (var x = 0; x < size; x++) {
      for (var y = 0; y <= size - 11; y++) {
        if (checkPat(pat1, function (i) { return mat.m[i][x]; }, y)) s += 40;
        if (checkPat(pat2, function (i) { return mat.m[i][x]; }, y)) s += 40;
      }
    }
    // Rule 4: balance dark/light
    var dark = 0;
    for (var y = 0; y < size; y++) for (var x = 0; x < size; x++) if (mat.m[y][x]) dark++;
    var pct = Math.floor(100 * dark / (size * size));
    var pctA = pct - (pct % 5);
    var pctB = pctA + 5;
    s += Math.min(Math.abs(pctA - 50), Math.abs(pctB - 50)) / 5 * 10;
    return s;
  }

  function build(text) {
    var bytes = utf8Bytes(text);
    var ver = pickVersion(bytes.length);
    var size = 17 + 4 * ver;
    var mat = newMatrix(size);

    // Functional patterns
    placeFinder(mat, 0, 0);
    placeFinder(mat, size - 7, 0);
    placeFinder(mat, 0, size - 7);
    // Separators (already accounted for in placeFinder via reserved area with light modules)
    // Actually placeFinder marks 8x8 with a border of light. Explicit separators not needed here.

    // Timing patterns
    placeTiming(mat);

    // Alignment patterns (for v >= 2)
    var pos = ALIGN[ver - 1];
    if (pos) {
      for (var a = 0; a < pos.length; a++) {
        for (var b = 0; b < pos.length; b++) {
          var cx = pos[a], cy = pos[b];
          // Skip positions overlapping finder patterns
          if ((cx <= 8 && cy <= 8) ||
              (cx <= 8 && cy >= size - 9) ||
              (cx >= size - 9 && cy <= 8)) continue;
          placeAlignment(mat, cx, cy);
        }
      }
    }

    // Reserve format info area
    reserveFormat(mat);

    // Place data
    var cw = buildDataCodewords(text, ver);
    placeDataBits(mat, cw);

    // Try all 8 masks, pick best score
    var savedM = [];
    for (var y = 0; y < size; y++) savedM.push(mat.m[y].slice());
    var bestMask = 0, bestScore = Infinity;
    for (var mk = 0; mk < 8; mk++) {
      // Restore
      for (var y = 0; y < size; y++) mat.m[y].set(savedM[y]);
      applyMask(mat, mk);
      writeFormat(mat, mk);
      var sc = score(mat);
      if (sc < bestScore) { bestScore = sc; bestMask = mk; }
    }
    // Apply best mask final
    for (var y = 0; y < size; y++) mat.m[y].set(savedM[y]);
    applyMask(mat, bestMask);
    writeFormat(mat, bestMask);
    return mat;
  }

  function svg(text, opts) {
    opts = opts || {};
    var margin = opts.margin != null ? opts.margin : 4;
    var size = opts.size != null ? opts.size : 200;
    var mat = build(text);
    var n = mat.size;
    var vb = n + 2 * margin;
    var scale = size / vb;
    var parts = [];
    parts.push('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ' + vb + ' ' + vb + '" width="' + (vb * scale).toFixed(0) + '" height="' + (vb * scale).toFixed(0) + '" shape-rendering="crispEdges" role="img" aria-label="Cod QR pentru URL-ul lecției">');
    parts.push('<rect width="100%" height="100%" fill="#fff"/>');
    var path = "";
    for (var y = 0; y < n; y++) {
      for (var x = 0; x < n; x++) {
        if (mat.m[y][x]) {
          path += "M" + (x + margin) + " " + (y + margin) + "h1v1h-1z";
        }
      }
    }
    parts.push('<path d="' + path + '" fill="#000"/>');
    parts.push('</svg>');
    return parts.join("");
  }

  root.QR = { svg: svg, build: build };
})(typeof window !== "undefined" ? window : this);

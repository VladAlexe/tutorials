/* ===========================================================================
   Tema deschisa / intunecata

   Se include cu <script src="..." defer></script> inaintea randarii, ca sa nu
   clipeasca. Alegerea se tine in localStorage; fara alegere, se ia preferinta
   sistemului.
   =========================================================================== */

(function(){
  const CHEIE = "dsw.tema";
  let aleasa = null;
  try { aleasa = localStorage.getItem(CHEIE); } catch {}
  if (aleasa === "deschis" || aleasa === "intunecat")
    document.documentElement.setAttribute("data-tema", aleasa);

  window.dswTema = {
    curenta(){
      const a = document.documentElement.getAttribute("data-tema");
      if (a) return a;
      return matchMedia("(prefers-color-scheme: dark)").matches ? "intunecat" : "deschis";
    },
    comuta(){
      const noua = this.curenta() === "intunecat" ? "deschis" : "intunecat";
      document.documentElement.setAttribute("data-tema", noua);
      try { localStorage.setItem(CHEIE, noua); } catch {}
      document.dispatchEvent(new CustomEvent("dsw:tema", { detail: noua }));
      return noua;
    }
  };
})();

/* ===========================================================================
   Manualul: cuprins care urmărește secțiunea curentă. Atât.
   Fără porți, fără blocaje: aici se citește, nu se predă.
   =========================================================================== */

export function porneste(capitol){
  const sectiuni = [...document.querySelectorAll(".tut__s")];
  const legaturi = [...document.querySelectorAll(".tut__nav a")];
  if (!sectiuni.length) return;

  const dupaId = new Map(legaturi.map(a => [a.getAttribute("href").slice(1), a]));
  const obs = new IntersectionObserver(intrari => {
    intrari.forEach(it => {
      if (!it.isIntersecting) return;
      legaturi.forEach(a => a.classList.remove("activ"));
      dupaId.get(it.target.id)?.classList.add("activ");
    });
  }, { rootMargin: "-12% 0px -76% 0px" });
  sectiuni.forEach(s => obs.observe(s));

  /* se marchează ca citit, ca să se vadă în progres că a reluat materialul */
  import("/data-science-workflows/js/colectare.js?v=5")
    .then(m => m.marcheazaSectiune(`${capitol}/manual`))
    .catch(() => {});
}

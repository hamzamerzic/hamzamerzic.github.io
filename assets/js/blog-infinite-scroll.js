/*
 * Progressive-enhancement infinite scroll for the paginated blog listing.
 * As the reader nears the bottom, the next page's .blog-card items are fetched
 * and appended to the CSS-grid, following the pagination chain until it ends.
 * The numbered pagination is hidden while this is active but kept in the DOM as
 * a no-JS (and on-error) fallback. No-ops on any page without a next link.
 */
(function () {
  "use strict";

  const grid = document.querySelector(".blog-card-grid");
  const pagination = document.querySelector("nav[aria-label='Blog page navigation']");
  if (!grid || !pagination) return;

  // The next-page link is the last .page-item; skip when it's disabled (last page).
  function nextUrlFrom(scope) {
    const nav = scope.querySelector("nav[aria-label='Blog page navigation']");
    if (!nav) return null;
    const items = nav.querySelectorAll(".page-item");
    const last = items[items.length - 1];
    if (!last || last.classList.contains("disabled")) return null;
    const link = last.querySelector("a.page-link");
    return link ? link.href : null;
  }

  let nextUrl = nextUrlFrom(document);
  if (!nextUrl) return; // single page — leave pagination as-is

  pagination.style.display = "none";

  const sentinel = document.createElement("div");
  sentinel.className = "blog-scroll-sentinel";
  sentinel.setAttribute("aria-hidden", "true");
  grid.after(sentinel);

  let loading = false;

  function stop(restorePagination) {
    observer.disconnect();
    sentinel.remove();
    if (restorePagination) pagination.style.display = "";
  }

  async function loadNext() {
    if (loading || !nextUrl) return;
    loading = true;
    try {
      const res = await fetch(nextUrl, { credentials: "same-origin" });
      if (!res.ok) throw new Error("HTTP " + res.status);
      const doc = new DOMParser().parseFromString(await res.text(), "text/html");
      doc.querySelectorAll(".blog-card-grid > .blog-card").forEach(function (card) {
        grid.appendChild(document.importNode(card, true));
      });
      nextUrl = nextUrlFrom(doc);
      if (!nextUrl) stop(false);
    } catch (e) {
      stop(true); // restore real pagination so navigation still works
    } finally {
      loading = false;
    }
  }

  var observer = new IntersectionObserver(
    function (entries) {
      if (entries.some((e) => e.isIntersecting)) loadNext();
    },
    { rootMargin: "600px 0px" }
  );
  observer.observe(sentinel);
})();

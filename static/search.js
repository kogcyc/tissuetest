async function runSearch() {
  const res = await fetch('/search_index.json');
  const index = await res.json();

  // Create input box
  const input = document.createElement('input');
  input.type = 'text';
  input.placeholder = 'Search (e.g. "cnc dropout")';
  input.style = 'width: 100%; padding: 0.5rem; font-size: 1rem;';
  document.getElementById('searchbox').appendChild(input);

  // Create results display
  const resultsDiv = document.getElementById('results');

  input.addEventListener('input', () => {
    const query = input.value.toLowerCase().trim();
    const terms = query.split(/\s+/).filter(Boolean); // skip empty strings

    const results = index.filter(entry =>
      terms.every(term =>
        entry.keywords.some(kw => kw.includes(term))
      )
    );

    resultsDiv.innerHTML = results.length
      ? results.map(r => `<p><a href="${r.url}">${r.title}</a></p>`).join('')
      : '<p><em>No matches</em></p>';
  });
}

runSearch();

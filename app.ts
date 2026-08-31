document.addEventListener('DOMContentLoaded', () => {
  const container = document.getElementById('app') || document.body;

  const title = document.createElement('h1');
  title.innerText = 'Tabela e Jogos - Série A';
  container.appendChild(title);

  const standingsButton = document.createElement('button');
  standingsButton.innerText = 'Carregar Tabela';
  container.appendChild(standingsButton);

  const matchesButton = document.createElement('button');
  matchesButton.innerText = 'Carregar Jogos';
  container.appendChild(matchesButton);

  const resultsDiv = document.createElement('div');
  resultsDiv.id = 'results';
  container.appendChild(resultsDiv);

  standingsButton.addEventListener('click', async () => {
    try {
      resultsDiv.innerText = 'Carregando tabela...';
      const response = await fetch('/api/serie-a/standings');
      const data = await response.json();
      resultsDiv.innerHTML = `<pre>${JSON.stringify(data, null, 2)}</pre>`;
    } catch (error) {
      resultsDiv.innerText = 'Erro ao carregar tabela.';
    }
  });

  matchesButton.addEventListener('click', async () => {
    try {
      resultsDiv.innerText = 'Carregando jogos...';
      const response = await fetch('/api/serie-a/matches');
      const data = await response.json();
      resultsDiv.innerHTML = `<pre>${JSON.stringify(data, null, 2)}</pre>`;
    } catch (error) {
      resultsDiv.innerText = 'Erro ao carregar jogos.';
    }
  });
});
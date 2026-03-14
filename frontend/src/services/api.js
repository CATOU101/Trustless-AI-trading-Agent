const BASE_URL = "http://localhost:8000";

async function parseResponse(response) {
  if (!response.ok) {
    const errorBody = await response.text();
    throw new Error(errorBody || `Request failed with status ${response.status}`);
  }
  return response.json();
}

export async function getPortfolio() {
  const response = await fetch(`${BASE_URL}/portfolio`);
  return parseResponse(response);
}

export async function getAgentDecision(coin) {
  const response = await fetch(`${BASE_URL}/agent/analyze`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({ coin })
  });
  return parseResponse(response);
}

export async function getLatestDecision(asset = "bitcoin") {
  const response = await fetch(`${BASE_URL}/agent/decision`);
  if (response.ok) {
    return parseResponse(response);
  }
  return getAgentDecision(asset);
}

export async function getTradeHistory() {
  const response = await fetch(`${BASE_URL}/trades`);
  return parseResponse(response);
}

export async function getAgentLeaderboard() {
  const response = await fetch(`${BASE_URL}/agents/leaderboard`);
  return parseResponse(response);
}

export async function getAgentVotes(coin) {
  const response = await fetch(
    `${BASE_URL}/agents/decisions?coin=${encodeURIComponent(coin)}`
  );
  return parseResponse(response);
}

export async function getMarketData(asset) {
  const response = await fetch(
    `${BASE_URL}/market/price/${encodeURIComponent(asset)}`
  );
  return parseResponse(response);
}

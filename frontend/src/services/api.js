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

export async function getTradeHistory() {
  const response = await fetch(`${BASE_URL}/trades`);
  return parseResponse(response);
}

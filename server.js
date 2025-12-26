const express = require('express');
const axios = require('axios');
const cors = require('cors');
const fs = require('fs');
const path = require('path');
const app = express();
const PORT = process.env.PORT || 3000;

// Middleware
app.use(cors());
app.use(express.json());

// Load data from files
let logs = [];
let bans = [];
try {
  logs = JSON.parse(fs.readFileSync('logs.json', 'utf8')) || [];
  bans = JSON.parse(fs.readFileSync('bans.json', 'utf8')) || [];
} catch (e) {
  // Files not exist, start empty
}

// Save to files function
const saveData = () => {
  fs.writeFileSync('logs.json', JSON.stringify(logs, null, 2));
  fs.writeFileSync('bans.json', JSON.stringify(bans, null, 2));
};

// Save PID
fs.writeFileSync('server.pid', process.pid.toString());

// User request: log + check ban + get info
app.post('/request', async (req, res) => {
  const { username, num } = req.body;
  if (!username || !num) return res.status(400).json({ error: 'Username and num required' });

  // Check ban
  if (bans.some(b => b.username === username)) {
    return res.json({ banned: true });
  }

  // Log request
  logs.push({ username, num, timestamp: new Date().toISOString() });
  saveData();

  // Fetch from API
  try {
    const apiResponse = await axios.get(`https://x2-proxy.vercel.app/api?num=${num}`);
    res.json(apiResponse.data);
  } catch (error) {
    res.json([]);
  }
});

// Admin endpoints
app.get('/logs', (req, res) => res.json(logs.slice(-100))); // Last 100
app.get('/bans', (req, res) => res.json(bans));
app.post('/ban', (req, res) => {
  const { username } = req.body;
  if (!username) return res.status(400).json({ error: 'Username required' });
  bans.push({ username, timestamp: new Date().toISOString() });
  saveData();
  // Delete user file if exists
  const userFile = `${username}_user.sh`;
  if (fs.existsSync(userFile)) {
    fs.rmSync(userFile);
  }
  res.json({ status: `User ${username} banned` });
});
app.post('/unban', (req, res) => {
  const { username } = req.body;
  const index = bans.findIndex(b => b.username === username);
  if (index === -1) return res.status(404).json({ error: 'User not banned' });
  bans.splice(index, 1);
  saveData();
  res.json({ status: `User ${username} unbanned` });
});

app.listen(PORT, () => {
  console.log(`Codex NumInfo server with admin on port ${PORT}`);
});

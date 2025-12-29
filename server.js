const express = require('express');
const axios = require('axios');
const fs = require('fs');
const app = express();
app.use(express.json());

const PORT = process.env.PORT || 3000;
const BANS_FILE = 'bans.json';
const LOGS_FILE = 'logs.json';

// Utility functions
const readData = (file) => fs.existsSync(file) ? JSON.parse(fs.readFileSync(file)) : [];
const writeData = (file, data) => fs.writeFileSync(file, JSON.stringify(data, null, 2));

app.post('/request', async (req, res) => {
    const { username, num } = req.body;
    
    // Check Ban
    const bans = readData(BANS_FILE);
    if (bans.includes(username)) {
        return res.json({ banned: true });
    }

    // Log Request
    const logs = readData(LOGS_FILE);
    logs.push({ username, num, time: new Date().toLocaleString() });
    writeData(LOGS_FILE, logs);

    try {
        const apiKey = "vishalboss_key_77f340c6e486ccceb64e242279b2bc9eee2c826f";
        const response = await axios.get(`https://numberimfo.vishalboss.sbs/api.php?number=${num}&key=${apiKey}`);
        res.json(response.data);
    } catch (error) {
        res.status(500).json({ error: "API Error" });
    }
});

// Admin Route: Ban User
app.post('/admin/ban', (req, res) => {
    const { username } = req.body;
    let bans = readData(BANS_FILE);
    if (!bans.includes(username)) {
        bans.push(username);
        writeData(BANS_FILE, bans);
    }
    res.json({ status: "success", message: `${username} banned.` });
});

// Admin Route: Get Logs
app.get('/admin/logs', (req, res) => {
    res.json(readData(LOGS_FILE));
});

app.listen(PORT, () => console.log(`Server running on port ${PORT}`));  // Check ban
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

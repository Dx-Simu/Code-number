const express = require('express');
const axios = require('axios');
const fs = require('fs');
const app = express();
app.use(express.json());

const BAN_FILE = 'banned_users.json';
const LOG_FILE = 'requests.json';

// ডাটা লোড ফাংশন
const loadData = (file) => {
    if (!fs.existsSync(file)) return [];
    return JSON.parse(fs.readFileSync(file));
};

app.post('/request', async (req, res) => {
    const { username, num } = req.body;
    
    // ব্যান চেক
    let bannedUsers = loadData(BAN_FILE);
    if (bannedUsers.includes(username)) {
        return res.json({ banned: true });
    }

    // রিকোয়েস্ট লগ সেভ
    let logs = loadData(LOG_FILE);
    logs.push({ username, number: num, time: new Date().toLocaleString() });
    fs.writeFileSync(LOG_FILE, JSON.stringify(logs, null, 2));

    try {
        const response = await axios.get(`https://numberimfo.vishalboss.sbs/api.php?number=${num}&key=vishalboss_key_77f340c6e486ccceb64e242279b2bc9eee2c826f`);
        res.json(response.data);
    } catch (error) {
        res.status(500).json({ error: "API Server Error" });
    }
});

// এডমিন রুট - লগ দেখার জন্য
app.get('/admin/logs', (req, res) => {
    res.json(loadData(LOG_FILE));
});

// ইউজার ব্যান করার রুট
app.post('/admin/ban', (req, res) => {
    const { targetUser } = req.body;
    let bannedUsers = loadData(BAN_FILE);
    if (!bannedUsers.includes(targetUser)) {
        bannedUsers.push(targetUser);
        fs.writeFileSync(BAN_FILE, JSON.stringify(bannedUsers));
    }
    res.json({ success: true });
});

app.listen(3000, () => console.log('Server running on port 3000'));

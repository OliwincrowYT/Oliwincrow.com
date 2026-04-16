import { kv } from '@vercel/kv';
import Pusher from 'pusher';

const pusher = new Pusher({
  appId: process.env.PUSHER_APP_ID,
  key: process.env.PUSHER_KEY,
  secret: process.env.PUSHER_SECRET,
  cluster: process.env.PUSHER_CLUSTER,
  useTLS: true,
});

export default async function handler(req, res) {
    const { method } = req;
    const ADMIN_EMAIL = process.env.ADMIN_EMAIL;
    const GOOGLE_CLIENT_ID = process.env.GOOGLE_CLIENT_ID;

    try {
        let userEmail = null;
        if (req.body?.token) {
            const payload = JSON.parse(Buffer.from(req.body.token.split('.')[1], 'base64').toString());
            userEmail = payload.email;
        }

        // --- MULTIPLAYER COMMANDS ---
        if (method === 'POST' && req.body.action === 'host_command') {
            const { command, value, room } = req.body;

            if (command === 'set_word') {
                // Automatic word validation via Dictionary API
                const dictRes = await fetch(`https://api.dictionaryapi.dev/api/v2/entries/en/${value}`);
                if (!dictRes.ok) return res.status(400).json({ error: "Word not found in dictionary" });

                await pusher.trigger(room, 'new-round', { word: value, host: userEmail });
                return res.status(200).json({ success: true });
            }
        }

        // --- LEADERBOARD & AUTH ---
        if (method === 'GET') {
            if (req.query.config === 'true') {
                return res.status(200).json({
                    clientId: GOOGLE_CLIENT_ID,
                    pusherKey: process.env.PUSHER_KEY,
                    pusherCluster: process.env.PUSHER_CLUSTER
                });
            }
            const { diff } = req.query;
            const topIds = await kv.zrange(`leaderboard:${diff}:ranks`, 0, 4, { rev: false });
            const results = [];
            for (const id of topIds) {
                const data = await kv.hget(`leaderboard:${diff}`, id);
                if (data) results.push(data.name, data.time);
            }
            return res.status(200).json(results);
        }

        if (method === 'POST') {
            const { name, diff, time } = req.body;
            if (!userEmail) return res.status(401).json({ error: "Auth required" });

            const memberId = `user:${userEmail}`;
            const existing = await kv.hget(`leaderboard:${diff}`, memberId);
            if (!existing || parseFloat(time) < existing.time) {
                await kv.hset(`leaderboard:${diff}`, { [memberId]: { time: parseFloat(time), name } });
                await kv.zadd(`leaderboard:${diff}:ranks`, { score: parseFloat(time), member: memberId });
            }
            return res.status(200).json({ success: true });
        }

        if (method === 'PUT') return res.status(200).json({ isAdmin: userEmail === ADMIN_EMAIL });

    } catch (error) {
        return res.status(500).json({ error: error.message });
    }
}
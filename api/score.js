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
    const { method, body, query } = req;
    const ADMIN_EMAIL = process.env.ADMIN_EMAIL;

    const getEmail = (token) => {
        try { return JSON.parse(Buffer.from(token.split('.')[1], 'base64').toString()).email; }
        catch { return null; }
    };

    try {
        if (method === 'GET' && query.config === 'true') {
            return res.status(200).json({
                clientId: process.env.GOOGLE_CLIENT_ID,
                pusherKey: process.env.PUSHER_KEY,
                pusherCluster: process.env.PUSHER_CLUSTER
            });
        }

        if (method === 'POST' && body.action === 'host_command') {
            const userEmail = getEmail(body.token);
            if (!userEmail) return res.status(401).json({ error: "Unauthorized" });

            if (body.command === 'set_word') {
                const dictRes = await fetch(`https://api.dictionaryapi.dev/api/v2/entries/en/${body.value}`);
                if (!dictRes.ok) return res.status(400).json({ error: "Invalid word" });

                await pusher.trigger(`room-${body.room}`, 'new-round', {
                    word: body.value,
                    host: userEmail
                });
                return res.status(200).json({ success: true });
            }
        }

        if (method === 'POST' && !body.action) {
            const { name, diff, time, token } = body;
            const userEmail = getEmail(token);
            if (!userEmail) return res.status(401).json({ error: "Auth required" });

            const memberId = `user:${userEmail}`;
            await kv.hset(`leaderboard:${diff}`, { [memberId]: { time: parseFloat(time), name } });
            await kv.zadd(`leaderboard:${diff}:ranks`, { score: parseFloat(time), member: memberId });
            return res.status(200).json({ success: true });
        }

        if (method === 'GET' && query.diff) {
            const topIds = await kv.zrange(`leaderboard:${query.diff}:ranks`, 0, 4, { rev: false });
            const results = [];
            for (const id of topIds) {
                const data = await kv.hget(`leaderboard:${query.diff}`, id);
                if (data) results.push(data.name, data.time);
            }
            return res.status(200).json(results);
        }

    } catch (error) {
        return res.status(500).json({ error: error.message });
    }
}
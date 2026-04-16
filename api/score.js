import { kv } from '@vercel/kv';

export default async function handler(req, res) {
    const { method } = req;
    const ADMIN_EMAIL = process.env.ADMIN_EMAIL;
    const GOOGLE_CLIENT_ID = process.env.GOOGLE_CLIENT_ID;

    try {
        let userEmail = null;
        if (req.body && req.body.token) {
            const payload = JSON.parse(Buffer.from(req.body.token.split('.')[1], 'base64').toString());
            userEmail = payload.email;
        }

        if (method === 'GET') {
            if (req.query.config === 'true') return res.status(200).json({ clientId: GOOGLE_CLIENT_ID });
            const { diff } = req.query;
            const topIds = await kv.zrange(`leaderboard:${diff}:ranks`, 0, 4, { rev: false });
            const results = [];
            for (const id of topIds) {
                const data = await kv.hget(`leaderboard:${diff}`, id);
                if (data) { results.push(data.name, data.time); }
            }
            return res.status(200).json(results);
        }

        if (method === 'POST') {
            const { name, diff, time } = req.body;
            if (!userEmail) return res.status(401).json({ error: "Login required" });
            const memberId = `user:${userEmail}`;
            const existingData = await kv.hget(`leaderboard:${diff}`, memberId);
            if (!existingData || parseFloat(time) < existingData.time) {
                await kv.hset(`leaderboard:${diff}`, { [memberId]: { time: parseFloat(time), name: name } });
                await kv.zadd(`leaderboard:${diff}:ranks`, { score: parseFloat(time), member: memberId });
            }
            return res.status(200).json({ success: true });
        }

        if (method === 'DELETE') {
            if (userEmail !== ADMIN_EMAIL) return res.status(403).json({ error: "Unauthorized" });
            await kv.del(`leaderboard:${req.body.diff}`, `leaderboard:${req.body.diff}:ranks`);
            return res.status(200).json({ success: true });
        }

        if (method === 'PUT') return res.status(200).json({ isAdmin: userEmail === ADMIN_EMAIL });
    } catch (error) {
        return res.status(500).json({ error: error.message });
    }
}
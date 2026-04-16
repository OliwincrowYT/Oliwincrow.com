import { kv } from '@vercel/kv';

export default async function handler(req, res) {
    const { method } = req;

    try {
        if (method === 'POST') {
            const { name, diff, time } = req.body;
            // Use a Sorted Set (ZADD) to store scores.
            // Redis automatically sorts these from lowest to highest.
            await kv.zadd(`leaderboard:${diff}`, {
                score: parseFloat(time),
                member: `${name}:${Date.now()}`
            });
            return res.status(200).json({ success: true });
        }

        if (method === 'GET') {
            const { diff } = req.query;
            // Get the top 5 fastest times
            const results = await kv.zrange(`leaderboard:${diff}`, 0, 4, {
                withScores: true,
                rev: false // false because lower time = better
            });

            return res.status(200).json(results);
        }
    } catch (error) {
        return res.status(500).json({ error: error.message });
    }
}
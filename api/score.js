import { kv } from '@vercel/kv';

export default async function handler(req, res) {
    const { method } = req;

    try {
        if (method === 'POST') {
            const { name, diff, time } = req.body;
            const numericTime = parseFloat(time);
            const key = `leaderboard:${diff}`;

            // 1. Check if this user already has a score in this category
            // We use the name as the member ID to make it unique per person
            const existingTime = await kv.zscore(key, name);

            // 2. Only update if they don't have a score, or if the new time is FASTER (lower)
            if (existingTime === null || numericTime < existingTime) {
                await kv.zadd(key, { score: numericTime, member: name });
                return res.status(200).json({ success: true, updated: true });
            }

            return res.status(200).json({ success: true, updated: false, msg: "Keep practicing! Previous time was faster." });
        }

        if (method === 'GET') {
            const { diff } = req.query;
            // Get top 5 fastest times
            const results = await kv.zrange(`leaderboard:${diff}`, 0, 4, {
                withScores: true,
                rev: false
            });

            return res.status(200).json(results);
        }
    } catch (error) {
        return res.status(500).json({ error: error.message });
    }
}
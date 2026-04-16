import { kv } from '@vercel/kv';

export default async function handler(req, res) {
    const { method } = req;
    const ADMIN_EMAIL = process.env.ADMIN_EMAIL; // Pull from Vercel Env

    try {
        if (method === 'POST') {
            // ... (Your existing POST logic)
        }

        if (method === 'GET') {
            // ... (Your existing GET logic)
        }

        if (method === 'DELETE') {
            const { token, diff } = req.body;
            const payload = JSON.parse(Buffer.from(token.split('.')[1], 'base64').toString());

            if (payload.email !== ADMIN_EMAIL) {
                return res.status(401).json({ error: "Unauthorized" });
            }

            await kv.del(`leaderboard:${diff}`);
            return res.status(200).json({ success: true });
        }

        // New helper for the frontend to check admin status
        if (method === 'PUT') {
            const { token } = req.body;
            const payload = JSON.parse(Buffer.from(token.split('.')[1], 'base64').toString());
            return res.status(200).json({ isAdmin: payload.email === ADMIN_EMAIL });
        }

    } catch (error) {
        return res.status(500).json({ error: error.message });
    }
}
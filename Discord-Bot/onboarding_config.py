GAME_ROLES = [
    ("Valorant", "🎯 Valorant", "Valorant chat, LFG, clips, and squad rooms."),
    ("Minecraft", "⛏️ Minecraft", "Minecraft chat, LFG, builds, and survival."),
    ("GTA V", "🚗 GTA V", "GTA chat, LFG, clips, and sessions."),
    ("CS2", "🔫 CS2", "Counter-Strike 2 chat, LFG, and competitive play."),
    ("Fortnite", "🪂 Fortnite", "Fortnite chat, LFG, and clips."),
    ("Roblox", "🧱 Roblox", "Roblox chat, LFG, and game recommendations."),
    ("Among Us", "👾 Among Us", "Among Us lobbies, LFG, and game nights."),
    ("Apex Legends", "🛡️ Apex Legends", "Apex chat, LFG, and squad building."),
    ("BGMI / PUBG", "🔫 BGMI / PUBG", "BGMI and PUBG chat, LFG, and squads."),
    ("Other Games", "🎮 Other Games", "Other games and gaming communities."),
]

AGE_ROLES = [
    ("Age 16–17", "16–17", "Optional age range."),
    ("Age 18–20", "18–20", "Optional age range."),
    ("Age 21–24", "21–24", "Optional age range."),
    ("Age 25+", "25+", "Optional age range."),
]

INTEREST_ROLES = [
    ("Gamer", "🎮 Gamer", "Gaming and community."),
    ("Developer", "💻 Developer", "Software and app development."),
    ("AI Enthusiast", "🤖 AI / ML", "AI, ML, LLMs, and automation."),
    ("UI/UX Designer", "🎨 Designer", "UI/UX, graphics, and visual design."),
    ("Content Creator", "🎥 Creator", "Streaming, videos, and content."),
    ("Student", "📚 Student", "Learning and building skills."),
    ("Entrepreneur", "💼 Entrepreneur", "Business and startups."),
    ("Freelancer", "🧑‍💻 Freelancer", "Independent and client work."),
    ("Tech Enthusiast", "⚡ Tech", "Technology and building things."),
]

NOTIFICATION_ROLES = [
    ("Announcements", "📢 Announcements", "Important server news."),
    ("Events", "🎟️ Events", "Community events."),
    ("New Projects", "🚀 New Projects", "New community projects."),
    ("Live / Stream", "🔴 Live / Stream", "Streams and live sessions."),
    ("Job Alerts", "💼 Job Alerts", "Jobs and opportunities."),
]

SELF_ASSIGNABLE_ROLE_NAMES = {
    role for role, _, _ in GAME_ROLES + AGE_ROLES + INTEREST_ROLES + NOTIFICATION_ROLES
} | {"Community"}

ONBOARDING_OPTIONS = [
    {"role": role, "label": label, "description": description}
    for role, label, description in GAME_ROLES + AGE_ROLES + INTEREST_ROLES + NOTIFICATION_ROLES
]

ONBOARDING_COPY = """# 👋 Welcome to Rupzha

## 🎮 Build your gaming profile
Choose the games you play. Your choices unlock the matching **game chats, LFG channels, clips, and voice rooms**.

### 🎯 Games
Pick every game you play. You can change these anytime.

### 🧑‍💻 Interests
Tell the community what else you're into.

### 🔔 Notifications
Choose what you actually want pinged for.

### 🎂 Age group
Optional. Choose a range if you're comfortable — never enter your exact age.

**Your choices are self-service. Staff, client, partnership, moderation, and security roles are never self-assignable.**
"""

WELCOME = """# 🎮 Welcome to RUPZHA

**Your gaming community. Your games. Your people.**

Rupzha is built around gaming, LFG, clips, events, squads, and community — with a professional staff layer behind it.

**Start here:**
> 📖 Read **𝗥𝘂𝗹𝗲𝘀**
> 🎮 Open **𝗖𝗵𝗼𝗼𝘀𝗲-𝗬𝗼𝘂𝗿-𝗥𝗼𝗹𝗲𝘀** and pick your games
> 💬 Meet people in **𝗚𝗲𝗻𝗲𝗿𝗮𝗹**
> 🔎 Find teammates in **𝗟𝗙𝗚**
> 🏆 Check **𝗘𝘃𝗲𝗻𝘁𝘀** for tournaments and game nights

Pick your games and the server will automatically show you the spaces that matter to you.
"""

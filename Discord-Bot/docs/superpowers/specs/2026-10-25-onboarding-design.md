# RupZha Onboarding Design

## Intent
Replace the basic game-role selector with a guided onboarding flow that collects useful profile preferences, assigns safe community roles, unlocks selected game hubs, and presents game choices with visual artwork.

## Goals
- Give new members a clear multi-step onboarding flow from `・𝗪𝗲𝗹𝗰𝗼𝗺𝗲`.
- Collect age range, optional gender, broad region, purposes, interests, games, and notification preferences.
- Never use age/gender as permission-bearing roles.
- Assign only non-privileged community/game/notification roles from onboarding.
- Keep staff roles fully manual.
- Show game visuals in the game-selection step.
- Keep the flow ephemeral so personal onboarding answers are not publicly posted.

## Non-goals
- Collect exact birth date, legal name, address, phone number, or other unnecessary personal information.
- Automatically grant staff, client, moderation, or private-workspace roles.
- Replace Discord's permission hierarchy with onboarding logic.

## Approach
A native RupZha bot-driven interactive onboarding flow is used instead of a second bot or a plain static selector. The bot owns the state for each active interaction, presents select menus/buttons ephemerally, then applies the selected non-privileged roles on completion. Game artwork is shown in the game step using externally hosted game-logo/image URLs.

## Flow
1. Welcome message → `Start Onboarding`.
2. Profile: age range, optional gender, broad region.
3. Purpose: gaming, teammates, friends, competitive, content, development/design, events, client/business, browsing.
4. Interests/skills: developer, web development, AI/ML, design, video editing, content, music, esports, tech, art, business, voice chat.
5. Games: existing RupZha game roles plus visual game cards.
6. Notifications: announcements, events, game updates, giveaways, community updates, or none.
7. Finish: keep `Member`, add `Verified` plus selected safe roles, and report the result ephemerally.

## Privacy / safety calls
- Age and gender are collected only for onboarding context and are not converted into visible roles.
- Region is broad and is not used for access control.
- The bot does not echo these profile answers into public channels.
- Existing strict role policy remains authoritative.

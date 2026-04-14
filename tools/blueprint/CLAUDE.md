# Blueprint - Prompt Generator for Claude Code

## Wat is het?
Blueprint is een interactieve wizard die gebruikers stap voor stap door vragen leidt en daar een gestructureerde, kant-en-klare Claude Code prompt van maakt.

## Bestanden
- `index.html` — volledige single-page app (HTML + CSS + JS in één bestand), dit is de hoofdversie
- `../../en/tools/blueprint/index.html` — Engelse versie (aparte kopie, niet automatisch gesynchroniseerd)
- `blueprint-hero.jpg` — OG/social share afbeelding
- `apple-touch-icon.png`, `favicon-*.png` — favicons

## Architectuur
- **Single-file SPA**: alle styling en logica zit in `index.html`
- **Multi-step wizard**: gebruiker doorloopt secties met vorige/volgende navigatie en progress dots
- **localStorage**: blueprints worden lokaal opgeslagen in een "library"; er is autosave/draft functionaliteit
- **Geen build stap**: direct te serveren als statisch bestand

## Design systeem
- Fonts: `Crimson Pro` (serif, body) + `Space Mono` (monospace, UI labels)
- CSS custom properties voor theming (zie `:root`)
- Dark mode via `prefers-color-scheme: dark`
- Kleurenpalet hoofdversie: `--forest: #1a3a6e` (blauw), `--bg: #fafafa`

## Conventies
- Alle wijzigingen aan de tool moeten in beide taalversies doorgevoerd worden (NL in `tools/blueprint/`, EN in `en/tools/blueprint/`)
- Houd alles in het enkele `index.html` bestand — geen aparte CSS/JS bestanden
- Test dark mode bij visuele wijzigingen
- Keyboard shortcuts en ARIA-attributen behouden voor accessibility

## URL's
- NL: `https://andreaswillemse.nl/tools/blueprint/`
- EN: `https://andreaswillemse.nl/en/tools/blueprint/`

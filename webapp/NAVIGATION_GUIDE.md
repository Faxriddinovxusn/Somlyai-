# Somly AI Navigation System

## 📱 Mobile Navigation (Bottom Tab Bar)

Fixed at the bottom of the screen on mobile devices (≤ 767px).

### Layout
```
[🏠]  [📄]  [➕]  [💸]  [⚙️]
 Bosh  Hisobot   Qarz   Sozl
```

### Navigation Items
| Icon | Label | Route | Description |
|------|-------|-------|-------------|
| 🏠 | Bosh sahifa | `/` | Dashboard & home |
| 📄 | Hisobotlar | `/stats` | Reports & statistics |
| ➕ | Yangi | onclick | Add new transaction |
| 💸 | Qarzlar | `/debts` | Debts tracking |
| ⚙️ | Sozlamalar | `/profile` | Settings & profile |

### Styling
- **Height**: 70px (including safe area)
- **Background**: Dark with blur (`rgba(0, 0, 0, 0.8)`)
- **Icons**: 22px (responsive to 24px on 480px+)
- **Active Color**: `--primary` (#0A84FF)
- **Transition**: 0.2s smooth ease
- **Rounded**: Yes (8-12px top corners)

### Plus Button (Center)
- **Size**: 50px (60x60 on tablets)
- **Shape**: Circle
- **Color**: Gradient (#0A84FF → #0052CC)
- **Shadow**: Multiple layers (10-14px blur)
- **Position**: Centered, floating up (-18px from bar)
- **On Hover**: Moves up, shadow increases
- **On Click**: Scale down 0.95, moves closer
- **Responsive**:
  - **Mobile**: 50px at -18px offset
  - **Tablet (480px+)**: 56px at -20px offset
  - **Desktop (1024px+)**: 64px at -24px offset

## 🖥️ Desktop/Tablet Navigation (Sidebar)

Fixed on the left side for tablets and desktop (≥ 768px).

### Sidebar Width
- **Base (Desktop)**: 240px
- **Tablet (768px+)**: 280px
- **Large (1024px+)**: 300px

### Layout
```
┌─────────────────┐
│ 💰 Somly AI     │  ← Logo section (top)
├─────────────────┤
│ ━━━ ASOSIY ━━━  │
│ 🏠 Bosh sahifa  │
│ 📄 Hisobotlar   │
│ 🏷 Kategoriyalar│
│ 💳 Balanslar    │
├─────────────────┤
│ ━━━ MOLIYA ━━━  │
│ 💸 Qarzlar      │
│ 📢 Obuna kanali │
├─────────────────┤
│ ━━━ IJTIMOIY ━━ │
│ 👥 Telegram ⤴  │
│ 🔔 Bildirishnoma│
├─────────────────┤
│ [spacer]        │  ← Flex spacer
├─────────────────┤
│ 🔵 [Name] ►     │  ← Profile (bottom)
│    Premium      │
└─────────────────┘
```

### Sections

#### Logo Section (Top)
- Logo icon (emoji or image)
- "Somly AI" text
- Padding: 24px
- Margin bottom: 32px
- Font size: 20px → 28px on desktop

#### Navigation Sections
Each section has:
- **Title**: Decorative separator (━━━ SECTION ━━━)
- **Links**: List of navigation items
- **Spacing**: 24px margin between sections

#### Profile Section (Bottom)
- Avatar with initials
- User name from Telegram
- Subscription status ("Premium")
- Hover effect (slight background change)
- Border top divider

### Navigation Links
All links have:
- **Icon**: 20px (left side)
- **Label**: 15px font, 500 weight
- **Active State**:
  - Background: `rgba(10, 132, 255, 0.15)`
  - Color: #0A84FF (primary blue)
- **Hover State**:
  - Background: `rgba(255, 255, 255, 0.08)`
  - Color: #FFFFFF
- **Transition**: 0.2s smooth ease
- **Padding**: 12px
- **Border Radius**: 12px (--radius-sm)
- **Gap**: 12px between icon and text

### External Links
Links to Telegram or external resources show a chevron icon (→) on the right.

## 🎨 Design System

### Colors
```
Primary: #0A84FF (iOS Blue) - Active state
Text Primary: #FFFFFF - Main text
Text Secondary: #8E8E93 - Inactive/muted text
Background: #000000 - Main background
Card: #1C1C1E - Sidebar/cards
Border: #2C2C2E - Borders
```

### Transitions
All interactive elements use:
- **Duration**: 0.2s (mobile) to 0.3s (desktop)
- **Timing**: `ease` or `cubic-bezier(0.4, 0, 0.2, 1)`

### Typography
- **Font Stack**: SF Pro Display → Inter → System fonts
- **Active Section**: Uppercase, smaller (12px)
- **Links**: 15px, 500 weight
- **Labels (Mobile)**: 10px, 500 weight

## 📱 Responsive Behavior

| Screen Size | Navigation | Behavior |
|---|---|---|
| ≤ 599px | Bottom Bar | Mobile optimized, 5 icons |
| 600-767px | Sidebar | Sidebar appears, bottom bar hidden |
| 768px+ | Sidebar | Full sidebar, optimized for tablet |
| 1024px+ | Sidebar | Expanded sidebar, plus button larger |

### Breakpoints
- **≤374px**: Extra small (iPhone SE)
- **375-479px**: Small (iPhone 6-8)
- **480-599px**: Medium (iPhone Plus)
- **600-767px**: Large (iPad mini)
- **768-1023px**: Extra large (iPad)
- **1024px+**: XXL (iPad Pro, desktop)

## ⌨️ Accessibility

### Touch Targets
- Minimum size: 48x48px
- All nav items meet this requirement
- Plus button is larger (50-64px)

### Keyboard Support
- All links are focusable
- Tab navigation works
- Enter/Space to activate

### ARIA Labels
- Navigation items have titles
- Plus button has aria-label
- External links marked with `target="_blank"`

## 🔄 Transitions

### Timing
- Color changes: 0.2s
- Transform (scale, translate): 0.2s
- Plus button hover: Full transform 0.2s

### Animation Details
```css
transition: all 0.2s ease;
transition: color 0.2s ease, transform 0.2s ease;
transition: background-color 0.2s ease;
```

## 📦 Components

### Files Modified
- `src/components/Sidebar.jsx` - Sidebar navigation
- `src/components/BottomBar.jsx` - Mobile bottom bar
- `src/index.css` - All styling

### Key CSS Classes
- `.sidebar` - Sidebar container
- `.sidebar-link` - Navigation links
- `.sidebar-profile` - Profile section
- `.bottom-nav` - Bottom bar
- `.nav-item` - Mobile nav items
- `.add-button` - Plus button
- `.avatar` - User avatar
- `.logo-image` - Logo icon

## 🔧 Customization

### Change Sidebar Width
Edit `:root`:
```css
--sidebar-width: 240px; /* Change this value */
```

### Change Colors
Edit `:root`:
```css
--primary: #0A84FF; /* Active color */
--bg: #000000; /* Background */
--card: #1C1C1E; /* Card background */
```

### Change Transition Speed
Edit relevant CSS rule:
```css
transition: all 0.2s ease; /* Change 0.2s to desired duration */
```

## 📝 Implementation Notes

- All navigation is reactive with React Router
- Active routes are auto-detected via `useLocation()`
- User info comes from Telegram Web App SDK
- Responsive design is mobile-first
- All transitions are GPU-accelerated
- SVG icons from Lucide React library

## ✅ Testing Checklist

- [x] Mobile bottom bar works (< 768px)
- [x] Desktop sidebar shows (≥ 768px)
- [x] Active route highlighting
- [x] Smooth transitions (0.2s)
- [x] Plus button styling and hover
- [x] Profile section displays correctly
- [x] Icons are properly sized
- [x] Text is readable in all sizes
- [x] Touch targets are adequate (48x48px+)
- [x] Responsive on all device sizes

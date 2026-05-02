# Somly AI - Apple Design System Guide

Telegram Mini App built with Apple's Human Interface Guidelines and dark theme principles.

## 🎨 Color Palette

### Apple Dark Theme (iOS-inspired)
```
--bg: #000000              /* Pure black background */
--card: #1C1C1E            /* Dark gray cards */
--border: #2C2C2E          /* Subtle borders */
--primary: #0A84FF         /* iOS Blue */
--success: #30D158         /* iOS Green (Income) */
--danger: #FF453A          /* iOS Red (Expense) */
--warning: #FFD60A         /* iOS Yellow (Debt) */
--text-primary: #FFFFFF    /* White text */
--text-secondary: #8E8E93  /* Light gray (subtitle) */
```

## 📐 Layout System

### Border Radius
- **Small elements**: `--radius-sm: 12px` (buttons, inputs, small cards)
- **Large elements**: `--radius-lg: 16px` (cards, modals, main containers)

### Typography
- **Font Stack**: `-apple-system, BlinkMacSystemFont, 'SF Pro Display', 'Segoe UI', Roboto, 'Inter', sans-serif`
- Uses SF Pro Display on iOS, falls back to Inter on other platforms
- All text is rendered with `-webkit-font-smoothing: antialiased` for crisp rendering

### Spacing
Mobile-first responsive approach:
- **Extra Small (≤374px)**: Compact spacing
- **Small (375-479px)**: iPhone standard
- **Medium (480-599px)**: iPhone Plus
- **Large (600-767px)**: Tablet mini
- **Extra Large (768-1023px)**: iPad
- **XXL (1024px+)**: Large tablets/desktop

## 📱 Responsive Design

The app automatically scales for different device sizes:

### iPhone SE (320px) 
- Minimal padding, compact layouts
- Single column, optimized bottom navigation

### iPhone 6-8 (375-414px)
- Standard iOS spacing and sizing
- Touch-friendly tap targets (48x48px minimum)

### iPad Mini/iPad (600px+)
- Sidebar appears instead of bottom navigation
- Wider content area with centered layout
- Multi-column layouts supported

### iPad Pro (1024px+)
- Full desktop layout
- Expanded sidebar (320px)
- Centered content with max-width constraints

## 🎯 Responsive Breakpoints

```css
/* Mobile-first approach */
320px  - Extra Small (iPhone SE)
375px  - Small (iPhone 6-8)
480px  - Medium (iPhone Plus)
600px  - Large (iPad mini)
768px  - Extra Large (iPad)
1024px - XXL (Large tablets, desktop)
```

## ✨ Design Principles

### 1. **Minimalism**
- Only necessary elements visible
- Clear hierarchy and spacing
- Plenty of whitespace

### 2. **Smooth Animations**
- All interactions use cubic-bezier timing functions
- Animations take 0.15-0.4s for smoothness
- Reduced motion support for accessibility

### 3. **Dark Theme Optimization**
- Pure black (#000000) background to save OLED power
- Reduced transparency for better readability
- High contrast for accessibility (WCAG AAA)

### 4. **Touch-First**
- Minimum touch target: 48x48px
- Fast, responsive feedback
- No hover-only interactions (works on mobile)

### 5. **Telegram Integration**
- Automatic expand() on app load
- Viewport change handling
- Safe area insets for notched devices
- Header and bottom bar color matching

## 🛠️ CSS Architecture

### Custom Properties (CSS Variables)
All design tokens are defined in `:root`:
```css
:root {
  /* Colors */
  --bg: #000000;
  --card: #1C1C1E;
  --primary: #0A84FF;
  
  /* Spacing & Sizing */
  --font-size-xs: 12px;
  --font-size-base: 16px;
  
  /* Borders */
  --radius-sm: 12px;
  --radius-lg: 16px;
}
```

### Reusable Utility Classes
- `.card` - Styled container
- `.button`, `.btn-primary` - Button styles
- `.text-secondary` - Muted text
- `.flex-between` - Flex layout utility
- `.title`, `.subtitle` - Typography utilities

### Animations
- `fade-in` - Smooth entrance
- `slide-down-enter` - List item animation
- `slide-up` - Modal entrance
- `number-enter/exit` - Value transitions
- `dot-pulse` - Live update indicator

## 📋 Implementation Checklist

✅ **Color System**
- Color palette implemented with CSS variables
- All color references use variables (except basic white/black)

✅ **Typography**
- SF Pro Display/Inter font stack configured
- Responsive font sizes for all device classes

✅ **Layout**
- Mobile-first responsive grid
- Flexbox-based layout system
- Safe area insets for notched devices

✅ **Navigation**
- Bottom navigation for mobile (≤767px)
- Sidebar navigation for tablet+ (≥768px)
- Active state indicators

✅ **Telegram SDK**
- `expand()` called immediately on load
- Viewport change handling
- Theme colors set to black

✅ **Animations**
- Smooth transitions (0.15-0.4s)
- Cubic-bezier timing functions
- Reduced motion support

✅ **Accessibility**
- Minimum touch targets (48x48px)
- High contrast (WCAG AAA)
- Semantic HTML with ARIA labels
- Keyboard navigation support

## 🚀 Performance Optimizations

1. **GPU-Accelerated Animations**
   - Transform and opacity for smooth 60fps
   - will-change hints for heavy animations

2. **CSS Variables**
   - Single-source-of-truth for design tokens
   - Easy theme switching capability

3. **Mobile Optimization**
   - Minimal bundle size
   - Touch-optimized (no hover delay)
   - Viewport optimization

4. **Print Styles**
   - Hidden navigation for printing
   - White background for better ink usage

## 🎮 Interactive Elements

### Buttons
- **Primary**: `--primary` color with white text
- **Hover/Active**: Scale to 0.96 with smooth transition
- **TAP**: Immediate visual feedback on touch

### Input Fields
- Background: `--bg` with `--border` outline
- Focus: Blue border with subtle shadow
- Placeholder: `--text-secondary` color

### Cards
- Background: `--card` with 1px `--border`
- Rounded: `--radius-lg` (16px)
- Shadow: Subtle elevation effect

## 📱 Safe Area Handling

Automatic safe area insets for notched/dynamic island devices:
```css
padding: max(0px, env(safe-area-inset-*))
```

This ensures content is not hidden behind notches or home indicators.

## 🔄 Future Enhancements

- [ ] Light theme variant
- [ ] Custom theme colors (per-user settings)
- [ ] Animation preferences toggle
- [ ] Font size adjustment
- [ ] High contrast mode option
- [ ] RTL language support improvements

## 📚 Reference Links

- [Apple Human Interface Guidelines](https://developer.apple.com/design/human-interface-guidelines/)
- [Telegram WebApp Documentation](https://core.telegram.org/bots/webapps)
- [WCAG 2.1 Accessibility Guidelines](https://www.w3.org/WAI/WCAG21/quickref/)

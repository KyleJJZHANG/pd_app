# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

# Project Summary
The "Psychological Duck" project is a web application that provides emotional support and memory healing through interactive features. Users can converse with a duck character, explore emotional narratives via an interactive map, store personal memories, and access multimedia resources. The application leverages modern web technologies to enhance emotional well-being, offering a unique blend of companionship and self-reflection.

# Project Module Description
The application includes several key modules:
- **Chat Module**: Engage in interactive conversations with the duck character, featuring personalized responses and emotion analysis.
- **Map Exploration Module**: Navigate various scenes that narrate stories related to users' emotional journeys.
- **Memory Archive Module**: A space for users to store and reflect on personal memories, categorized and searchable.
- **Multimedia Resources**: Access comics and videos to enrich the emotional companionship experience.
- **Profile Management Module**: Manage user profiles, settings, and data.
- **Emotion Reporting Module**: Analyze user emotions and display reports based on interactions.

## Development Commands

**Package Manager**: pnpm (required - see package.json)

```bash
# Install dependencies
pnpm i

# Start development server
pnpm run dev

# Build for production
pnpm run build

# Lint code (ESLint)
pnpm run lint

# Preview production build
pnpm run preview
```

## Architecture Overview

This is a **心理鸭 (Psychological Duck)** therapy/wellness app - a React SPA with a therapeutic chat interface, map exploration, and memory preservation features. The app is designed as an MVP frontend-only implementation using localStorage for persistence.

### Technology Stack
- **Frontend**: React 18 + TypeScript + Vite
- **UI Framework**: shadcn/ui components + Tailwind CSS
- **Routing**: React Router DOM
- **State Management**: React built-in (useState/useContext) + localStorage
- **Build Tool**: Vite with SWC
- **Styling**: Tailwind CSS with custom duck-themed color palette

### Core Application Structure

**Main Pages** (Bottom Navigation):
- `/` - Home page with dynamic duck character and daily warm quotes
- `/chat` - Chat interface with therapeutic duck responses + media content
- `/map` - Virtual map exploration with calming scenes and interactions
- `/memories` - Memory preservation wall where users can save and view memories
- `/profile` - User profile (referenced in Layout but not implemented)

**Key Services**:
- `StorageService` (singleton): Manages localStorage for messages, memories, timeline, user preferences
- `EmotionAnalyzer` (singleton): Analyzes user text input for emotions using keyword patterns and sentiment analysis

**Data Models** (see `src/data/index.ts`):
- `Message`: Chat messages with optional panel/video content
- `Scene`: Map exploration scenes with interactions
- `MemoryItem`: User-created memory cards
- `TimelineEntry`: Unified timeline linking all user activities
- `EmotionTag`/`EmotionStats`: Emotion analysis results

### Content Resources
- **Comics**: Should be placed in `/public/panels/` as individual page images
- **Videos**: Should be placed in `/public/videos/` as 10-30 second clips
- **Static Assets**: Lake background, duck imagery in `/public/images/`

### Design System
**Colors** (Duck-themed palette):
- Duck Yellow: `#F7D774` / Duck White: `#FFF7E8`
- Lake Blue: `#A5D8E2`, Grass Green: `#C8E6C9`
- Warm Orange: `#F5A25D`, Hat Blue: `#4A90E2`
- Background: Sky gradient (light blue → cream white)

**UI Patterns**:
- Comic-style speech bubbles for chat
- Watercolor aesthetics with rounded corners
- Gentle animations (fade in/out, slight floating effects)
- Large touch-friendly components for mobile-first design

### Local Storage Schema
- `duck_messages`: Array of Message objects
- `duck_memories`: Array of MemoryItem objects  
- `duck_timeline`: Array of TimelineEntry objects (sorted by date)
- `duck_user_prefs`: User preferences object

### Path Aliases
- `@/` points to `src/` directory (configured in vite.config.ts)

## Important Implementation Notes

1. **Chinese Language**: App content is primarily in Chinese - maintain this for user-facing text
2. **Therapeutic Focus**: This is a mental wellness app - maintain gentle, supportive tone in all interactions
3. **Mobile-First**: UI is designed for mobile with bottom navigation and touch-friendly components
4. **No Backend**: Pure frontend app using localStorage - no API calls expected
5. **Emotion Analysis**: Built-in Chinese keyword-based emotion detection system
6. **Media Integration**: Chat and map features integrate comic panels and video content dynamically

## File Organization Patterns

- `/src/components/ui/` - shadcn/ui components (pre-installed)
- `/src/components/` - Custom application components  
- `/src/pages/` - Route page components
- `/src/services/` - Business logic services (StorageService, EmotionAnalyzer)
- `/src/data/` - TypeScript interfaces and static data
- `/src/hooks/` - Custom React hooks
- `/public/panels/` - Comic page images
- `/public/videos/` - Short video clips

## Mobile-First Layout Optimizations (Recent Updates)

### 1. Layout Scroll Management (Layout.tsx)
**Problem**: Scroll bars extended to bottom navigation, affecting mobile UX
**Solution**: 
- Changed container from `min-h-screen` to `h-screen` for fixed height
- Added `overflow-y-auto` to main content area for independent scrolling
- Added `pb-20` bottom padding to prevent content occlusion by navigation bar
- Implemented route-based scroll position reset using `useEffect` + `mainRef.scrollTop = 0`

**Result**: Clean scrolling experience with navigation bar always visible and stable

### 2. Immersive Chat Experience (App.tsx + Chat.tsx)
**Problem**: Chat page had bottom navigation bar, reducing immersion
**Solution**:
- Modified route structure: Chat page (`/chat`) extracted from Layout wrapper
- Other pages remain within Layout for normal navigation
- Added smart back button in Chat header with `useNavigate(-1)` for intelligent return
- Chat now displays full-screen without bottom navigation interference

**Result**: Full immersive chat experience similar to modern messaging apps

### 3. Mobile-Optimized Emotion Report (EmotionReport.tsx)
**Problem**: Emotion report used desktop-style dialog, poor mobile experience
**Solution**:
- Converted from dialog overlay to full-screen page layout
- Replaced backdrop/modal with `fixed inset-0` full-screen container
- Added mobile-friendly header with back button (ArrowLeft icon)
- Implemented independent content scrolling with `flex-1 overflow-y-auto`
- Maintained all existing functionality while improving mobile UX

**Result**: Native app-like emotion report experience on mobile devices

### 4. Navigation Flow Improvements
- Intelligent back navigation throughout the app
- Consistent header patterns for full-screen pages
- Smooth route transitions with scroll position management
- Mobile-first interaction patterns

### 5. TypeScript Fixes
- Added missing `EmotionTag` and `EmotionStats` interfaces to `src/data/index.ts`
- Implemented complete emotion analytics system in StorageService
- Fixed type errors in Chat.tsx timeline entries

### 6. Layout Height Conflict Resolution
**Problem**: Double height setting causing unexpected scrollbars in pages
**Root Cause**: 
- Layout.tsx sets `h-screen` container with `pb-20` (80px bottom padding)
- Child pages (like Home.tsx) also set `h-screen` causing height overflow
- Result: Page height (100vh) + Layout padding (80px) > Available viewport height

**Solution Pattern**:
```tsx
// ❌ Wrong - causes height overflow
<div className="h-screen">  {/* Child page */}
  {/* Content */}
</div>

// ✅ Correct - adapts to available space  
<div className="h-full">    {/* Child page */}
  {/* Content */} 
</div>
```

**Layout Structure Understanding**:
```
Layout (h-screen)
├── main (flex-1, overflow-y-auto, pb-20)
│   └── Page Component (h-full) ← Should adapt to main's space
└── Bottom Navigation (fixed, ~80px height)
```

**Fixed in**: Home.tsx - Changed from `h-screen` to `h-full` and optimized spacing

## Development Practices

- Use TypeScript interfaces from `src/data/index.ts` for type safety
- Leverage existing StorageService methods for data persistence
- Follow shadcn/ui component patterns for consistent styling
- Use EmotionAnalyzer for any text sentiment features
- Maintain duck-themed color palette and gentle UI animations
- Test localStorage functionality across browser sessions
- **Mobile-First**: Always consider mobile UX when designing layouts and interactions
- **Immersive Experience**: Use full-screen layouts for primary user flows (chat, reports)
- **Smart Navigation**: Implement intelligent back navigation with `useNavigate(-1)`
- **Height Management**: Use `h-full` in child pages, `h-screen` only in Layout component
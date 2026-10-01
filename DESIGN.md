---
name: AI Email Assistant
description: A calm, high-trust workspace for turning email into clear action.
colors:
  action-blue: "#155eef"
  action-blue-hover: "#004ee8"
  midnight-nav: "#101828"
  canvas: "#f3f5f7"
  surface: "#ffffff"
  ink: "#111827"
  secondary-ink: "#667085"
  line: "#dfe3e8"
  success: "#027a48"
  warning: "#b54708"
  danger: "#b42318"
typography:
  headline:
    fontFamily: "Avenir Next, Avenir, PingFang SC, Noto Sans CJK SC, sans-serif"
    fontSize: "clamp(25px, 2.2vw, 32px)"
    fontWeight: 720
    lineHeight: 1.18
    letterSpacing: "-0.035em"
  body:
    fontFamily: "Avenir Next, Avenir, PingFang SC, Noto Sans CJK SC, sans-serif"
    fontSize: "15px"
    fontWeight: 400
    lineHeight: 1.55
  label:
    fontFamily: "Avenir Next, Avenir, PingFang SC, Noto Sans CJK SC, sans-serif"
    fontSize: "12px"
    fontWeight: 650
rounded:
  sm: "7px"
  md: "11px"
spacing:
  sm: "8px"
  md: "16px"
  lg: "24px"
components:
  button-primary:
    backgroundColor: "{colors.action-blue}"
    textColor: "{colors.surface}"
    rounded: "{rounded.sm}"
    padding: "9px 15px"
    height: "40px"
  card:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.ink}"
    rounded: "{rounded.md}"
    padding: "24px"
---

# Design System: AI Email Assistant

## Overview

**Creative North Star: "The Executive Mail Desk"**

The interface should feel like a precise, calm operations desk: dense enough for daily work, restrained enough to keep attention on the messages and decisions. Deep midnight navigation establishes trust; bright action blue is reserved for actions and current state.

**Key Characteristics:**
- Compact, information-led composition
- Strong typographic hierarchy without decorative display effects
- Cool white surfaces separated by fine rules and restrained ambient depth
- Matching English and Chinese visual density

## Colors

The palette uses one clear action color against quiet cool neutrals. Semantic colors are reserved for status and risk.

**The One Action Color Rule.** Blue means navigation state, focus, links, or a user action; it is not decorative fill.

## Typography

**Display and Body Font:** Avenir Next with Avenir and CJK-native fallbacks.

Headlines use compact tracking and decisive weight. Body copy remains comfortable at 15px; labels are smaller and heavier for scanning tables and metadata.

**The Scan First Rule.** Data labels, status, senders, and dates must remain distinguishable at a glance in both languages.

## Layout

Content uses a centered 1216px workspace with 32px desktop gutters. Related metrics join into one segmented surface instead of unrelated floating tiles. At 1020px, metrics become two columns; at 560px, controls and metrics become single-column. Wide data tables scroll rather than compressing content past legibility.

## Elevation & Depth

Depth is ambient and restrained. Most hierarchy comes from tonal surfaces and one-pixel rules. Low shadows identify functional surfaces; medium shadow is reserved for focused entry experiences such as sign-in.

**The Flat Data Rule.** Rows and metric segments stay visually connected; they do not become individually floating cards.

## Shapes

Controls use gently curved 7px corners. Larger contained surfaces use 11px corners. Pills are limited to compact statuses, priorities, and language controls.

## Components

### Buttons
- Primary actions use action blue, white text, 7px corners, and a 40px minimum height.
- Ghost actions use a white surface and a cool gray border.
- Hover lifts by one pixel; focus always receives a visible blue ring.

### Cards / Containers
- Surfaces use white with a cool gray border and low ambient shadow.
- Segmented metric groups share an outer container and internal one-pixel dividers.

### Inputs / Fields
- Fields use white fill, strong gray borders, 7px corners, and an inset depth cue.
- Focus shifts the border and adds a three-pixel pale-blue ring.

### Navigation
- Global navigation uses a midnight bar, muted inactive labels, and a quiet filled active state with a thin blue underline.
- On narrow screens it remains one horizontal, scrollable line instead of wrapping into multiple rows.

## Do's and Don'ts

### Do:
- **Do** keep the highest priority action visually obvious on every page.
- **Do** use fine rules to organize dense email content.
- **Do** preserve visible focus and semantic status text alongside color.

### Don't:
- **Don't** decorate the interface with gradients, glass effects, or oversized empty cards.
- **Don't** use color without a navigation, action, focus, or status meaning.
- **Don't** hide long email content; wrap or scroll it predictably.

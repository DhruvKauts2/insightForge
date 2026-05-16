# ADR-0007: Next.js with TypeScript for the Dashboard Frontend

**Date:** 2026-05-16  
**Status:** Accepted

## Context

InsightForge needs a dashboard that renders time-series charts, tables of log entries, anomaly panels, and real-time updates via WebSocket. The primary users are engineers and on-call responders who need fast, interactive views. A static page or server-rendered template cannot support real-time chart updates without a client-side framework. The team needs type safety across a non-trivial component tree to avoid runtime bugs in data mapping between API responses and chart props.

## Decision

Use Next.js 14 (App Router) with TypeScript 5 and React 18 as the frontend framework. UI is styled with Tailwind CSS. Charts are rendered with Recharts (line, bar, pie). HTTP communication with the API uses Axios. WebSocket updates use `socket.io-client`. Icon set is Lucide React.

Pages:
- `/` — Home with KPI cards, log volume chart, service metrics, error distribution, and anomaly panel
- `/search` — Advanced log search interface
- `/anomalies` — Anomaly detection results

Auto-refresh is implemented with `setInterval` at 30–60 s per component; real-time events arrive via WebSocket.

## Consequences

**Positive**
- TypeScript prevents entire classes of runtime errors when mapping API responses to chart data types.
- Next.js App Router co-locates page components and layouts, reducing boilerplate.
- Recharts is declarative and integrates naturally with React state; adding a new chart type is a self-contained component.
- Tailwind CSS enables rapid UI iteration without context-switching to a separate stylesheet.
- Next.js can be incrementally adopted for SSR/SSG if SEO or initial load performance becomes a concern.

**Negative**
- `node_modules` is ~777 MB, making Docker image builds slow without a `.dockerignore` and multi-stage build that installs only production dependencies.
- Two separate refresh mechanisms (polling + WebSocket) need to be kept consistent; a component that polls and also listens on WebSocket may apply duplicate updates.
- Recharts does not support large datasets (thousands of points) efficiently in the browser; data must be pre-aggregated server-side.
- No state management library (Redux, Zustand, Jotai) is in place; as shared state grows across components, prop-drilling will become painful.

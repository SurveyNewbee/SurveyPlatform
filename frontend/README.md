# Frontend - Survey Platform UI

React application for the AI-powered survey platform.

## Setup (Coming Soon)

```bash
npm create vite@latest . -- --template react-ts
npm install
npm install react-router-dom
npm install -D tailwindcss postcss autoprefixer
npx tailwindcss init -p
```

## Planned Tech Stack

- **Framework:** React 18 + TypeScript
- **Routing:** React Router v6
- **Styling:** TailwindCSS
- **Charts:** Recharts (for reporting phase)
- **Forms:** React Hook Form
- **State:** React Context (simple for MVP)
- **API Client:** Fetch API with custom wrapper

## Project Structure

```
frontend/
├── src/
│   ├── pages/
│   │   ├── Dashboard.tsx
│   │   ├── Setup.tsx
│   │   ├── Editor.tsx
│   │   ├── Preview.tsx
│   │   ├── Launch.tsx
│   │   ├── Status.tsx
│   │   └── Report.tsx
│   ├── components/
│   │   ├── layout/
│   │   │   ├── Header.tsx
│   │   │   ├── Breadcrumb.tsx
│   │   │   └── Navigation.tsx
│   │   ├── survey/
│   │   │   ├── QuestionCard.tsx
│   │   │   ├── SectionNav.tsx
│   │   │   └── LOISlider.tsx
│   │   └── common/
│   │       ├── Button.tsx
│   │       ├── Input.tsx
│   │       └── Modal.tsx
│   ├── api/
│   │   └── client.ts
│   ├── types/
│   │   └── survey.ts
│   ├── App.tsx
│   └── main.tsx
└── package.json
```

## Development Phases

### Phase 0: Foundation (Week 1-2)
- [ ] Initialize Vite project
- [ ] Set up TailwindCSS
- [ ] Create routing structure
- [ ] Build global header
- [ ] Build Dashboard page

### Phase 1a: Setup Page (Week 2-3)
- [ ] Brief input textarea
- [ ] File upload
- [ ] Extraction progress
- [ ] Structured form fields
- [ ] Wire to backend API

### Phase 2: LOI Slider (Week 4-5)
- [ ] Slider component
- [ ] Question visibility logic
- [ ] Pin/exclude controls
- [ ] Focus note display

### Phase 3: Editor (Week 5-6)
- [ ] Question card component
- [ ] Inline editing
- [ ] Add/delete/reorder
- [ ] Skip logic editor

### Phase 4: Preview (Week 7-9)
- [ ] Respondent view rendering
- [ ] Comment system
- [ ] AI edit flow
- [ ] Diff view

### Phase 5: Reporting (Week 9-12)
- [ ] Chart components
- [ ] Cross-tabulation
- [ ] Export functions

### Phase 6: Launch (Week 12-13)
- [ ] Launch wizard
- [ ] Status page

## Running Development Server

```bash
npm run dev
```

## Next Steps

1. Initialize Vite project
2. Install dependencies
3. Create basic routing
4. Build header component
5. Build Dashboard skeleton

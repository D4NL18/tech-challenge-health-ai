# 4. Frontend and Angular

*Read this in other languages: [English](4-frontend-angular.md) | [Português](../docs/4-frontend-angular.md)*

In this document, I detail the architectural decisions of the user interface (Frontend). The goal was to build a clean, responsive, and reliable clinical interface using **Angular 18+**, without relying on generic pre-built UI bundles like Bootstrap or Tailwind.

---

## 4.1. Single Page Application (SPA)
Angular compiles the client into a Single Page Application. From the hosting perspective (Firebase Hosting), only one static `index.html` file is served.

All navigation happens directly in the client's browser. When the clinician switches between Anamnesis triage, Medical Routes, or the Admin Dashboard, the page never triggers a full refresh. Angular swaps components in and out of the DOM instantaneously, delivering a fast, desktop-grade user experience.

---

## 4.2. Standalone Components
The application is built entirely using Angular's modern **Standalone Components** architecture (eliminating legacy `NgModule` boilerplate):
*   Every component (e.g., `medical-routes.component.ts`, `admin-dashboard.component.ts`) explicitly declares its own dependencies (`CommonModule`, `FormsModule`, `RouterModule`).
*   Enables fine-grained **Tree Shaking** during production builds, pruning unused code.
*   Significantly accelerates first contentful paint and modular lazy loading.

---

## 4.3. Form System (Two-Way Binding and Reactive Controls)
Clinical triage forms require flexible, dynamic validation:
*   Template-driven two-way binding (`[(ngModel)]`) binds form inputs directly to TypeScript model states.
*   The UI dynamically adjusts input fields based on the selected disease context (e.g., swapping breast cancer cytology biomarkers for PCOS hormonal panels).
*   Dedicated validation slots enforce valid numerical boundaries before allowing submission.

---

## 4.4. The Service Layer (Services and HttpClient)
UI components follow the *Single Responsibility Principle*: they render templates and handle user interactions, but never make raw HTTP calls directly.

Network interactions are encapsulated in dedicated Services (`inference.service.ts` and `routes.service.ts`):
1. The component passes raw form inputs to the service.
2. The service constructs the `FormData` multipart payload (attaching x-ray image binaries and clinical symptom JSONs) or structured JSON routing requests.
3. The service calls FastAPI endpoints via Angular's `HttpClient`.
4. The service handles HTTP error interceptors and returns RxJS `Observable` streams.
5. The component subscribes to the stream and updates its local reactive state when responses arrive.

---

## 4.5. Styling: "Prontuário" Clinical Design System, SCSS Tokens & BEM
Rather than using generic external CSS libraries, we designed the **"Prontuário" Clinical Design System**, formally documented in `.agents/docs/design/DESIGN_SYSTEM.md` and showcased in the interactive specimen `.agents/docs/design/specimen/prontuario-kit.html`.

### Visual Foundations:
- **Clinical Typography Triad:**
  - `Source Serif 4`: Clinical headers, section titles, and diagnostic summaries, imparting editorial authority.
  - `Public Sans`: Form labels, buttons, navigation items, and interactive UI controls for crisp readability.
  - `IBM Plex Mono`: Telemetry, coordinates, risk percentages, transit times, and tabular data using tabular figures (`font-variant-numeric: tabular-nums`).
- **Physical Elevation & Dual-Layer Shadows:**
  Scale ranging from `--shadow-0` (flat surface with hairline borders) to `--shadow-4` (sliding audit drawers), eliminating artificial neon glows or diffuse blurs.
- **Mechanical Motion Choreography:**
  GPU-composited transitions (`transform` and `opacity`), mechanical button recess (`translateY(1px)` on `:active`), and strict accessibility collapsing via `@media (prefers-reduced-motion: reduce)`.
- **BEM Methodology (Block, Element, Modifier):**
  - **Block:** Structural component, e.g., `.c-card`, `.c-button`
  - **Element:** Internal constituent part, e.g., `.c-card__header`, `.c-button__label`
  - **Modifier:** Variant or state, e.g., `.c-button--secondary`, `.c-badge--urgent`

---

## 4.6. Medical Routing Module & Leaflet.js (`pages/medical-routes/`)
**Reference Component:** `frontend/src/app/pages/medical-routes/medical-routes.component.ts`

In Phase 2, a dedicated route (`/routes`) provides a full hospital logistics dispatch dashboard:
- **Interactive Leaflet.js Map:** Renders customized markers (green for central hospital/depot, red/orange for urgent home care visits numbered with stop sequence) and plots real street polylines computed by OSRM.
- **Genetic Parameter Tuning Panel:** Allows operators to tune population size (10 to 200), generations (10 to 100), mutation rates, and clinical urgency penalty weights.
- **Instant Demo Scenario:** A "Load Demo Scenario" button immediately populates realistic patient stops (with cold-chain requirements, time windows, and clinical priority weights).
- **Integrated LLM Logistics Assistant:** Tabbed interface featuring "Turn-by-Turn Driver Instructions", "Field Dispatch Chat", and "Executive Hospital Report".

---

## 4.7. Genetic Algorithm Benchmark Audit on Admin Dashboard
**Reference Component:** `frontend/src/app/pages/admin-dashboard/admin-dashboard.component.ts`

The administrative dashboard consumes the genetic experiment telemetry endpoint (`GET /api/v1/anamnesis/admin/genetic-experiments`) to display:
- Direct comparison between the Phase 1 GridSearch baseline and the 3 Genetic Algorithm experiments.
- Visual cards highlighting percentage gains in $F_2$-Score and Recall (clinical reduction of False Negatives).
- Clear explanation of the weighted clinical fitness formula and hyperparameter evolution trajectories.

---

## 4.8. Clinical Explainability Report with LLM
**Reference Component:** `frontend/src/app/pages/anamnesis/anamnesis.component.ts`

Following multimodal triage:
- A prominent button allows clinicians to request "Generate Clinical Explanation (LLM - Phase 2)".
- The synthesized report renders in a structured clinical card with distinct sections: Diagnostic Summary, Key Risk Factors, Suggested Clinical Actions, and Ethical AI Disclaimers.

---

**Next Step:**
To see how models are trained and managed in MLOps pipelines outside the API, access [5-mlops-training.md](./5-mlops-training.md).

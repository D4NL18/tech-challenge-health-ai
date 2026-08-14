# 4. Frontend and Angular

*Read this in other languages: [English](4-frontend-angular.md) | [Português](../docs/4-frontend-angular.md)*

In this document, I detail the architectural decisions of the user interface (Frontend). The goal was to create a user-friendly, fast, and scalable screen using **Angular**, without relying on heavy pre-built CSS frameworks.

---

## 4.1. Single Page Application (SPA)
Angular compiles everything into a Single Page Application. This means that, from the Server's perspective (Firebase Hosting), there is only one generic `index.html` file.

All the magic happens in the user's browser via JavaScript. When the doctor transitions between the "Make Diagnosis" screen and the "Settings (Admin)" screen, the page does not blink or reload. Angular simply erases the old component from memory and draws the new one instantly. This dramatically increases the perception of speed.

---

## 4.2. Standalone Components
In older versions of Angular, there was a concept called `NgModule`, where all components had to be declared in a massive central file. This was very verbose and made code reuse difficult.

In this project, I used the modern Angular approach: **Standalone Components**.
Each component (e.g., `admin-dashboard.component.ts`) is self-sufficient. It imports only what it needs to use (e.g., `CommonModule`, `FormsModule`). This generates the following benefits:
*   Makes the code much cleaner.
*   Allows for more efficient **Tree Shaking** (Angular deletes unused code during the final build).
*   Improves application loading time (easier Lazy Loading).

---

## 4.3. Form System (Reactive Forms and ngModel)
Filling out the anamnesis is the core of the platform.

For the Artificial Intelligence form, I used `ngModel` (Template-driven Forms) to facilitate the direct binding of variables between the HTML and the Typescript (Two-Way Data Binding).
This allows me, for example, to dynamically change the questions that appear on the screen depending on whether the user selected "Evaluate Breast Cancer" or "Evaluate PCOS" in the main selector.

---

## 4.4. The Service Layer (Services and HttpClient)
The `anamnesis.component.ts` file (Component) does not know what my Backend URL is, nor how the network works. It only knows how to draw buttons on the screen and react to clicks.

The one who manages the internet call is the **Service** (`inference.service.ts`).
This architecture respects the *Single Responsibility Principle*.

1. When the patient clicks "Submit", the Component passes the raw data to the Service.
2. The Service builds the `FormData` in **Multipart** format (attaching the x-ray image and a JSON with the symptoms).
3. The Service uses Angular's native `HttpClient` class to hit the FastAPI API.
4. The Service handles network problems (if the server is down) and returns an *Observable*.
5. The Component listens to the *Observable* and only updates the screen to show the results when the data arrives.

---

## 4.5. Styling: SCSS and BEM Standard
I did not use Bootstrap or Tailwind. I preferred to have total layout control by creating a **Custom Design System** written purely in SCSS.

SCSS allows me to create variables (e.g., `$color-primary`) and calculation functions (e.g., lighten colors by X%).

To avoid a mess of classes in the CSS, I applied the **BEM Methodology** (Block, Element, Modifier).
*   **Block:** The parent element, e.g., `.card`
*   **Element:** A child of the parent, e.g., `.card__title`
*   **Modifier:** A state, e.g., `.card--highlighted`

This guarantees that the CSS class of the Admin screen button will never break or overwrite the CSS class of the Main screen button.

---

**Next Step:**
To see how the AI was trained and managed outside the web API, access [5-mlops-treinamento.md](./5-mlops-treinamento.md).

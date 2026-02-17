# Frontend UI/UX Standards

## 1. Design System
Based on `Element Plus` component library with custom theme configuration.

### 1.1 Color Palette
- **Primary Color**: `#1890ff` (Brand Blue)
- **Functional Colors**:
    - **Success**: `#52c41a`
    - **Warning**: `#faad14`
    - **Error**: `#ff4d4f`
- **Neutral Colors**:
    - **Text Primary**: `#000000` (85% opacity)
    - **Text Secondary**: `#000000` (45% opacity)
    - **Border**: `#d9d9d9`
    - **Background**: `#f0f2f5` (Layout BG), `#ffffff` (Component BG)

### 1.2 Typography
- **Font Family**: `PingFang SC`, `Helvetica Neue`, `Arial`, sans-serif.
- **Font Sizes**:
    - **H1**: 48px
    - **H2**: 36px
    - **H3**: 24px
    - **Body**: 14px (Base)
    - **Small**: 12px
- **Line Height**: 1.5 - 1.8
- **Font Weight**: 400 (Regular), 500 (Medium), 600 (Semi-bold).

### 1.3 Layout & Grid
- **Grid System**: 24-column grid.
- **Breakpoints**:
    - `xs`: <576px
    - `sm`: ≥576px
    - `md`: ≥768px
    - `lg`: ≥992px
    - `xl`: ≥1200px
- **Content Width**: Max-width `1440px` for main content area.
- **Spacing**: Base unit `8px`. (8, 16, 24, 32, 48).

## 2. Component Specifications

### 2.1 Tables
- **Default Height**: `400px` with virtual scrolling for large datasets (>1000 rows).
- **Pagination**: Sticky at bottom.
- **Actions**: Right-aligned column with icons/links.

### 2.2 Forms
- **Label Width**: Fixed `120px`.
- **Validation**: Real-time validation with inline error messages.
- **Buttons**:
    - **Primary**: Main action (Save, Submit).
    - **Default**: Secondary action (Cancel, Reset).
    - **Text**: Less prominent actions (View details).

### 2.3 Charts (ECharts)
- **Tooltip**: Always enabled, formatted values.
- **Legend**: Bottom or Top-Right.
- **DataZoom**: Enabled for time-series charts (x-axis).
- **Color Theme**: Consistent with System Palette.

## 3. Interaction Design
- **Loading State**: Skeleton screens for initial load. Spinners for button actions.
- **Feedback**:
    - **Success**: Toast notification (Auto-dismiss 3s).
    - **Error**: Modal dialog with `Trace ID` for support.
- **Persistence**: List pages must remember `page`, `pageSize`, and `filter` params in URL or LocalStorage.
- **Export**: Built-in support for CSV/XLSX export on all data tables.

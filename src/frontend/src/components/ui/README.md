# UI Components

Bộ UI components có thể tái sử dụng cho claudeminder frontend với hiệu ứng glassmorphism và neon.

## Components

### GlassCard

Container có hiệu ứng glassmorphism với backdrop-filter blur.

**Props:**

- `children`: React.ReactNode - Nội dung bên trong card
- `className?`: string - CSS class tùy chỉnh
- `blur?`: 'light' | 'medium' | 'heavy' - Mức độ blur (mặc định: 'medium')
  - light: 8px
  - medium: 16px
  - heavy: 24px
- `border?`: boolean - Hiển thị border (mặc định: true)
- `onClick?`: () => void - Click handler

**Ví dụ:**

```tsx
import { GlassCard } from "./components/ui";

<GlassCard blur="heavy" border={true}>
  <h3>Card Title</h3>
  <p>Card content</p>
</GlassCard>;
```

### NeonText

Text component với hiệu ứng neon glow sử dụng text-shadow.

**Props:**

- `children`: React.ReactNode - Nội dung text
- `className?`: string - CSS class tùy chỉnh
- `color?`: 'accent' | 'success' | 'warning' | 'danger' | 'custom' - Màu sắc (mặc định: 'accent')
- `customColor?`: string - Màu tùy chỉnh (hex/rgb)
- `intensity?`: 'low' | 'medium' | 'high' - Độ sáng (mặc định: 'medium')
- `animated?`: boolean - Animation pulse (mặc định: false)
- `as?`: 'h1' | 'h2' | ... | 'span' - HTML tag (mặc định: 'span')

**Ví dụ:**

```tsx
import { NeonText } from './components/ui';

<NeonText color="success" intensity="high" animated>
  High Usage Alert
</NeonText>

<NeonText customColor="#00ff00" intensity="medium" as="h1">
  Custom Color
</NeonText>
```

### CircularProgress

Circular SVG progress indicator với hiển thị phần trăm ở giữa.

**Props:**

- `percentage`: number - Giá trị phần trăm (0-100)
- `size?`: number - Kích thước (px, mặc định: 120)
- `strokeWidth?`: number - Độ dày đường viền (mặc định: 8)
- `className?`: string - CSS class tùy chỉnh
- `showPercentage?`: boolean - Hiển thị % ở giữa (mặc định: true)
- `color?`: 'accent' | 'success' | 'warning' | 'danger' | 'auto' - Màu (mặc định: 'auto')
  - auto: Tự động chọn màu dựa trên percentage
    - < 50%: success (green)
    - 50-80%: warning (yellow)
    - > 80%: danger (red)
- `animated?`: boolean - Animation (mặc định: true)

**Ví dụ:**

```tsx
import { CircularProgress } from './components/ui';

<CircularProgress percentage={75} size={150} strokeWidth={10} />
<CircularProgress percentage={95} color="danger" />
```

### GaugeProgress

Gauge/speedometer style progress indicator với arc 0-180 độ.

**Props:**

- `percentage`: number - Giá trị phần trăm (0-100)
- `size?`: number - Kích thước (px, mặc định: 200)
- `className?`: string - CSS class tùy chỉnh
- `showValue?`: boolean - Hiển thị giá trị (mặc định: true)
- `label?`: string - Nhãn phía dưới
- `animated?`: boolean - Animation (mặc định: true)

**Features:**

- Arc từ -90° đến 90° (semicircle)
- Gradient từ green → yellow → red
- Kim xoay theo giá trị percentage
- Center dot và value text

**Ví dụ:**

```tsx
import { GaugeProgress } from './components/ui';

<GaugeProgress percentage={65} label="CPU Usage" />
<GaugeProgress percentage={95} size={250} label="Critical" />
```

## CSS Variables

Các components sử dụng CSS variables để tùy chỉnh màu sắc:

```css
:root {
  --accent: #646cff;
  --bg-secondary: rgba(0, 0, 0, 0.1);
  --success: #22c55e;
  --warning: #f59e0b;
  --danger: #ef4444;
  --text-primary: #1a1a1a;
  --text-secondary: #666;
}
```

## Dark Mode

Tất cả components đều hỗ trợ dark mode tự động thông qua `prefers-color-scheme`.

## Demo

Xem file `demo.tsx` để xem ví dụ sử dụng tất cả components.

```bash
# Import demo component
import { UIDemo } from './components/ui/demo';

# Use in your app
<UIDemo />
```

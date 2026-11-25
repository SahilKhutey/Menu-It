# FCD-08 §11 — Component API Reference

## 1. Layout Components

### Container (`<Container>`)
| Prop | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `size` | `'sm' \| 'md' \| 'lg' \| 'xl' \| 'full'` | `'lg'` | Maximum layout container width |
| `className` | `string` | `undefined` | Additional CSS classes |

### Grid (`<Grid>`)
| Prop | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `columns` | `1 \| 2 \| 3 \| 4 \| 6 \| 12 \| ResponsiveCols` | `1` | Column configuration |
| `gap` | `'none' \| 'xs' \| 'sm' \| 'md' \| 'lg' \| 'xl'` | `'md'` | Gutter spacing between cells |

### Stack (`<Stack>`)
| Prop | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `direction` | `'vertical' \| 'horizontal'` | `'vertical'` | Flex direction |
| `align` | `'start' \| 'center' \| 'end' \| 'stretch'` | `'stretch'` | Cross-axis alignment |
| `gap` | `'none' \| 'xs' \| 'sm' \| 'md' \| 'lg' \| 'xl'` | `'md'` | Flex item gap spacing |
| `wrap` | `boolean` | `false` | Whether to wrap child items |

---

## 2. Interactive & Display Components

### Button (`<Button>`)
| Prop | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `variant` | `'primary' \| 'secondary' \| 'outline' \| 'ghost' \| 'destructive'` | `'primary'` | Visual intent styling |
| `size` | `'sm' \| 'md' \| 'lg'` | `'md'` | Touch target and typography size |
| `isLoading` | `boolean` | `false` | Shows loading spinner and disables clicks |
| `leftIcon` / `rightIcon` | `ReactNode` | `undefined` | Optional icons |

### Input (`<Input>`)
| Prop | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `label` | `string` | `undefined` | Associated form label |
| `error` | `string` | `undefined` | Validation error message |
| `helperText` | `string` | `undefined` | Descriptive helper message |

### Badge (`<Badge>`)
| Prop | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `variant` | `'default' \| 'primary' \| 'success' \| 'warning' \| 'destructive' \| 'outline'` | `'default'` | Semantic coloring |

### Dialog (`<Dialog>`)
| Prop | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `isOpen` | `boolean` | **Required** | Visibility control |
| `onClose` | `() => void` | **Required** | Close handler (backdrop or Esc key) |
| `title` | `string` | `undefined` | Accessible dialog heading |
| `description` | `string` | `undefined` | Accessible dialog description |

### Tabs (`<Tabs>`)
| Prop | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `defaultValue` | `string` | **Required** | Initial active tab identifier |
| `onValueChange` | `(value: string) => void` | `undefined` | Change callback |

# ARC-08 §4 — Design Token Architecture

## 1. Token Taxonomy
Design tokens are organized into 6 strictly governed hierarchical namespaces:
1. `color`:
   - `brand`: `primary`, `secondary`, `accent`
   - `surface`: `default`, `subtle`, `raised`
   - `text`: `primary`, `secondary`, `inverse`
   - `border`: `default`, `subtle`
   - `status`: `success`, `warning`, `error`
2. `typography`:
   - `fontFamily`: `body`, `heading` (whitelisted system & Google fonts: Inter, Playfair Display, Cinzel, Montserrat, Plus Jakarta Sans, Lora, Poppins, Merriweather)
   - `fontSize`: `small`, `body`, `heading`, `display`
   - `fontWeight`: `normal` (400), `medium` (500), `bold` (700)
3. `spacing`: `xs` (0.25rem), `sm` (0.5rem), `md` (1rem), `lg` (1.5rem), `xl` (2rem), `2xl` (3rem)
4. `radius`: `none` (0px), `small` (0.25rem), `medium` (0.375rem/0.5rem), `large` (0.75rem), `full` (9999px)
5. `shadow`: `none`, `sm`, `card`
6. `elevation`: Level 0 to Level 3

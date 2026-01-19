use image::{Rgba, RgbaImage};
use tauri::image::Image;

/// Generate a tray icon with usage percentage text overlay
pub fn generate_percentage_icon(percentage: u8) -> Image<'static> {
    let size = 22u32; // Standard tray icon size
    let mut img = RgbaImage::new(size, size);

    // Background color based on usage level
    let bg_color = if percentage > 80 {
        Rgba([220, 53, 69, 255])   // Red
    } else if percentage > 60 {
        Rgba([255, 193, 7, 255])   // Yellow
    } else {
        Rgba([40, 167, 69, 255])   // Green
    };

    // Fill background circle
    let center = (size / 2) as f32;
    let radius = (size / 2 - 1) as f32;

    for y in 0..size {
        for x in 0..size {
            let dx = x as f32 - center;
            let dy = y as f32 - center;
            if dx * dx + dy * dy <= radius * radius {
                img.put_pixel(x, y, bg_color);
            }
        }
    }

    // Draw percentage text (simplified - just show number)
    // For production, consider using a font rendering library
    let text = if percentage >= 100 { "!".to_string() } else { format!("{}", percentage) };
    draw_text_centered(&mut img, &text, size);

    let pixels = img.into_raw();
    Image::new_owned(pixels, size, size)
}

fn draw_text_centered(img: &mut RgbaImage, text: &str, size: u32) {
    let white = Rgba([255, 255, 255, 255]);
    let center_x = size / 2;
    let center_y = size / 2;

    // Simple bitmap font for digits (3x5 pixels each)
    let digits: [[[u8; 3]; 5]; 11] = [
        // 0
        [[1,1,1], [1,0,1], [1,0,1], [1,0,1], [1,1,1]],
        // 1
        [[0,1,0], [1,1,0], [0,1,0], [0,1,0], [1,1,1]],
        // 2
        [[1,1,1], [0,0,1], [1,1,1], [1,0,0], [1,1,1]],
        // 3
        [[1,1,1], [0,0,1], [1,1,1], [0,0,1], [1,1,1]],
        // 4
        [[1,0,1], [1,0,1], [1,1,1], [0,0,1], [0,0,1]],
        // 5
        [[1,1,1], [1,0,0], [1,1,1], [0,0,1], [1,1,1]],
        // 6
        [[1,1,1], [1,0,0], [1,1,1], [1,0,1], [1,1,1]],
        // 7
        [[1,1,1], [0,0,1], [0,0,1], [0,0,1], [0,0,1]],
        // 8
        [[1,1,1], [1,0,1], [1,1,1], [1,0,1], [1,1,1]],
        // 9
        [[1,1,1], [1,0,1], [1,1,1], [0,0,1], [1,1,1]],
        // ! (exclamation for 100%)
        [[0,1,0], [0,1,0], [0,1,0], [0,0,0], [0,1,0]],
    ];

    let char_width = 3;
    let char_height = 5;
    let spacing = 1;

    let total_width = text.len() as u32 * (char_width + spacing) - spacing;
    let start_x = center_x.saturating_sub(total_width / 2);
    let start_y = center_y.saturating_sub(char_height / 2);

    for (i, c) in text.chars().enumerate() {
        let digit_idx = match c {
            '0'..='9' => c as usize - '0' as usize,
            '!' => 10,
            _ => continue,
        };

        let offset_x = start_x + i as u32 * (char_width + spacing);

        for (row, line) in digits[digit_idx].iter().enumerate() {
            for (col, &pixel) in line.iter().enumerate() {
                if pixel == 1 {
                    let px = offset_x + col as u32;
                    let py = start_y + row as u32;
                    if px < size && py < size {
                        img.put_pixel(px, py, white);
                    }
                }
            }
        }
    }
}

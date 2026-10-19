#pragma once
// text_utils.h is included via ESPHome includes: directive (same compilation unit)

// Draw horizontal separator line across full display width
void draw_hline(esphome::display::Display *it, int y) {
  it->line(0, y, 960, y);
}

// Draw status bar (top 40px): time, temperature, humidity, wifi indicator
void draw_status_bar(esphome::display::Display *it,
                     esphome::font::Font *font,
                     esphome::font::Font *icon_font,
                     int hour, int minute,
                     float temp, float humidity,
                     bool wifi_connected) {
  it->printf(20, 8, font, "%02d:%02d", hour, minute);
  if (!isnan(temp)) {
    it->printf(700, 8, font, "%.1fC", temp);
  }
  if (!isnan(humidity)) {
    it->printf(840, 8, font, "%.0f%%", humidity);
  }
  if (wifi_connected) {
    it->printf(925, 8, icon_font, "\U000F05A9");
  }
  draw_hline(it, 40);
}

// Draw navigation bar (bottom 45px) with 4 page indicators
void draw_nav_bar(esphome::display::Display *it,
                  esphome::font::Font *font,
                  int current_page) {
  draw_hline(it, 495);
  const char *labels[] = {"Stroom", "Accu&Auto", "Lichten", "Airco"};
  for (int i = 0; i < 4; i++) {
    int cx = i * 240 + 120;
    int lw = GetTextBounds(it, font, labels[i]);
    int tw = 14 + lw;
    int sx = cx - tw / 2;
    if (i == current_page) {
      it->filled_circle(sx + 5, 518, 5);
    } else {
      it->circle(sx + 5, 518, 5);
    }
    it->print(sx + 14, 507, font, labels[i]);
  }
}

// Draw horizontal battery/progress bar with percentage fill
void draw_battery_bar(esphome::display::Display *it,
                      int x, int y, int w, int h,
                      float pct) {
  float c = pct < 0.0f ? 0.0f : (pct > 100.0f ? 100.0f : pct);
  it->rectangle(x, y, w, h);
  int fw = (int)((w - 4) * c / 100.0f);
  if (fw > 0) {
    it->filled_rectangle(x + 2, y + 2, fw, h - 4);
  }
}

// Draw large toggle button for lights page
void draw_light_button(esphome::display::Display *it,
                       int x, int y, int w, int h,
                       esphome::font::Font *icon_font,
                       const char *icon,
                       esphome::font::Font *label_font,
                       const char *line1,
                       const char *line2,
                       bool is_on) {
  if (is_on) {
    esphome::Color gray(0xC0, 0xC0, 0xC0);
    it->filled_rectangle(x + 1, y + 1, w - 2, h - 2, gray);
  }
  it->rectangle(x, y, w, h);
  it->printf(x + w / 2, y + 110, icon_font, TextAlign::CENTER, "%s", icon);
  it->printf(x + w / 2, y + 220, label_font, TextAlign::TOP_CENTER, "%s", line1);
  it->printf(x + w / 2, y + 265, label_font, TextAlign::TOP_CENTER, "%s", line2);
  it->printf(x + w / 2, y + h - 80, label_font, TextAlign::TOP_CENTER, "[%s]",
             is_on ? "AAN" : "UIT");
}

// Draw smaller mode/action button (for airco page)
void draw_mode_btn(esphome::display::Display *it,
                   int x, int y, int w, int h,
                   esphome::font::Font *font,
                   const char *label,
                   bool active) {
  if (active) {
    esphome::Color gray(0xC0, 0xC0, 0xC0);
    it->filled_rectangle(x + 1, y + 1, w - 2, h - 2, gray);
  }
  it->rectangle(x, y, w, h);
  it->printf(x + w / 2, y + h / 2, font, TextAlign::CENTER, "%s", label);
}

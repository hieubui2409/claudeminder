import { describe, it, expect, beforeEach, vi } from "vitest";
import { act } from "@testing-library/react";

// Reset zustand store state between tests
const mockLocalStorage: Record<string, string> = {};

vi.mock("zustand/middleware", async () => {
  const actual =
    await vi.importActual<typeof import("zustand/middleware")>(
      "zustand/middleware",
    );
  return {
    ...actual,
    persist: (config: unknown) => config,
  };
});

describe("themeStore", () => {
  beforeEach(async () => {
    vi.resetModules();
    // Clear mock localStorage
    Object.keys(mockLocalStorage).forEach(
      (key) => delete mockLocalStorage[key],
    );

    // Mock document.documentElement
    Object.defineProperty(document, "documentElement", {
      value: {
        className: "",
        style: {
          setProperty: vi.fn(),
        },
      },
      writable: true,
    });
  });

  it("has neon-dark as default theme", async () => {
    const { useThemeStore } = await import("../../src/stores/theme-store");
    const { theme } = useThemeStore.getState();
    expect(theme).toBe("neon-dark");
  });

  it("has basic as default color level", async () => {
    const { useThemeStore } = await import("../../src/stores/theme-store");
    const { colorLevel } = useThemeStore.getState();
    expect(colorLevel).toBe("basic");
  });

  it("sets theme correctly", async () => {
    const { useThemeStore } = await import("../../src/stores/theme-store");

    act(() => {
      useThemeStore.getState().setTheme("glass-light");
    });

    const { theme } = useThemeStore.getState();
    expect(theme).toBe("glass-light");
  });

  it("sets color level correctly", async () => {
    const { useThemeStore } = await import("../../src/stores/theme-store");

    act(() => {
      useThemeStore.getState().setColorLevel("advanced");
    });

    const { colorLevel } = useThemeStore.getState();
    expect(colorLevel).toBe("advanced");
  });

  it("sets accent color and applies to DOM in advanced mode", async () => {
    const { useThemeStore } = await import("../../src/stores/theme-store");
    const mockSetProperty = vi.fn();

    Object.defineProperty(document, "documentElement", {
      value: {
        className: "",
        style: { setProperty: mockSetProperty },
      },
      writable: true,
    });

    act(() => {
      useThemeStore.getState().setColorLevel("advanced");
      useThemeStore.getState().setAccentColor("#ff0000");
    });

    const { accentColor } = useThemeStore.getState();
    expect(accentColor).toBe("#ff0000");
    expect(mockSetProperty).toHaveBeenCalledWith("--accent", "#ff0000");
  });

  it("sets custom colors and applies to DOM in expert mode", async () => {
    const { useThemeStore } = await import("../../src/stores/theme-store");
    const mockSetProperty = vi.fn();

    Object.defineProperty(document, "documentElement", {
      value: {
        className: "",
        style: { setProperty: mockSetProperty },
      },
      writable: true,
    });

    act(() => {
      useThemeStore.getState().setColorLevel("expert");
      useThemeStore.getState().setCustomColors({
        bgPrimary: "#111111",
        textPrimary: "#ffffff",
      });
    });

    const { customColors } = useThemeStore.getState();
    expect(customColors.bgPrimary).toBe("#111111");
    expect(customColors.textPrimary).toBe("#ffffff");
    expect(mockSetProperty).toHaveBeenCalled();
  });

  it("applies theme class to document element", async () => {
    const { useThemeStore } = await import("../../src/stores/theme-store");

    act(() => {
      useThemeStore.getState().setTheme("minimal-light");
    });

    expect(document.documentElement.className).toBe("minimal-light");
  });

  it("handles system theme correctly", async () => {
    const { useThemeStore } = await import("../../src/stores/theme-store");

    act(() => {
      useThemeStore.getState().setTheme("system");
    });

    // Our mock matchMedia returns dark
    expect(document.documentElement.className).toBe("dark");
  });
});

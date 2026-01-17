import { renderHook, act } from "@testing-library/react";
import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { useCountdown } from "../../src/hooks/use-countdown";

describe("useCountdown", () => {
  beforeEach(() => {
    vi.useFakeTimers();
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  it("calculates remaining time correctly for 1 hour", () => {
    const targetDate = new Date(Date.now() + 3600000).toISOString();
    const { result } = renderHook(() => useCountdown(targetDate));

    expect(result.current.hours).toBe(1);
    expect(result.current.minutes).toBe(0);
    expect(result.current.seconds).toBe(0);
    expect(result.current.isExpired).toBe(false);
  });

  it("calculates remaining time correctly for 30 minutes", () => {
    const targetDate = new Date(Date.now() + 30 * 60 * 1000).toISOString();
    const { result } = renderHook(() => useCountdown(targetDate));

    expect(result.current.hours).toBe(0);
    expect(result.current.minutes).toBe(30);
    expect(result.current.isExpired).toBe(false);
  });

  it("updates every second", () => {
    const targetDate = new Date(Date.now() + 65000).toISOString();
    const { result } = renderHook(() => useCountdown(targetDate));

    expect(result.current.minutes).toBe(1);
    expect(result.current.seconds).toBe(5);

    act(() => {
      vi.advanceTimersByTime(1000);
    });

    expect(result.current.seconds).toBe(4);
  });

  it("sets isExpired when countdown reaches zero", () => {
    const targetDate = new Date(Date.now() + 1000).toISOString();
    const { result } = renderHook(() => useCountdown(targetDate));

    expect(result.current.isExpired).toBe(false);

    act(() => {
      vi.advanceTimersByTime(2000);
    });

    expect(result.current.isExpired).toBe(true);
    expect(result.current.totalSeconds).toBe(0);
  });

  it("returns correct humanReadable format for hours", () => {
    const targetDate = new Date(
      Date.now() + 2 * 3600000 + 30 * 60000,
    ).toISOString();
    const { result } = renderHook(() => useCountdown(targetDate));

    expect(result.current.humanReadable).toContain("h");
    expect(result.current.humanReadable).toContain("left");
  });

  it("returns correct humanReadable format for minutes only", () => {
    const targetDate = new Date(Date.now() + 15 * 60000 + 30000).toISOString();
    const { result } = renderHook(() => useCountdown(targetDate));

    expect(result.current.humanReadable).toContain("m");
    expect(result.current.humanReadable).toContain("s");
    expect(result.current.humanReadable).toContain("left");
  });

  it("returns 'Expired' when time is up", () => {
    const targetDate = new Date(Date.now() - 1000).toISOString();
    const { result } = renderHook(() => useCountdown(targetDate));

    expect(result.current.humanReadable).toBe("Expired");
  });

  it("handles past dates correctly", () => {
    const targetDate = new Date(Date.now() - 3600000).toISOString();
    const { result } = renderHook(() => useCountdown(targetDate));

    expect(result.current.totalSeconds).toBe(0);
    expect(result.current.isExpired).toBe(true);
  });

  it("recalculates when targetDate changes", () => {
    const initialTarget = new Date(Date.now() + 3600000).toISOString();
    const { result, rerender } = renderHook(
      ({ target }) => useCountdown(target),
      { initialProps: { target: initialTarget } },
    );

    expect(result.current.hours).toBe(1);

    const newTarget = new Date(Date.now() + 7200000).toISOString();
    rerender({ target: newTarget });

    expect(result.current.hours).toBe(2);
  });
});

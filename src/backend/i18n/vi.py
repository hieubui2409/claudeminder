"""Vietnamese language strings."""

STRINGS: dict[str, str] = {
    # General
    "app_name": "Claudiminder",
    "usage_title": "Sử dụng Claude",
    "loading": "Đang tải...",
    "error": "Lỗi",
    "success": "Thành công",

    # Reset countdown
    "reset_in": "Reset sau",
    "reset_complete": "Đã reset xong!",
    "hours": "giờ",
    "minutes": "phút",
    "seconds": "giây",

    # Offline mode
    "offline_mode": "Ngoại tuyến - hiển thị dữ liệu đã lưu",
    "connection_restored": "Đã kết nối lại",

    # Reminders
    "reminder_soon": "Token sẽ reset trong {minutes} phút!",
    "reminder_reset": "Token của bạn đã reset!",
    "reminder_threshold": "Đã sử dụng {percent}%",
    "reminder_snoozed": "Nhắc nhở đã tạm hoãn {minutes} phút",

    # Goals & Pace
    "pace_ok": "Đúng tiến độ",
    "pace_exceeded": "Đang dùng quá nhanh!",
    "budget_used": "Ngân sách: {used}% / {total}%",
    "daily_goal": "Mục tiêu ngày",

    # Focus mode
    "focus_mode_active": "Chế độ tập trung đang bật",
    "quiet_hours_active": "Giờ yên tĩnh đang bật",
    "dnd_active": "Không làm phiền (sử dụng > {threshold}%)",

    # TUI
    "press_q_quit": "Nhấn 'q' để thoát",
    "press_r_refresh": "Nhấn 'r' để làm mới",
    "press_h_help": "Nhấn 'h' để xem hướng dẫn",
    "refreshing": "Đang làm mới...",
    "last_updated": "Cập nhật lúc: {time}",

    # Usage metrics
    "five_hour_usage": "Sử dụng 5 giờ",
    "seven_day_usage": "Sử dụng 7 ngày",
    "extra_usage": "Sử dụng thêm",
    "utilization": "Mức sử dụng",
}

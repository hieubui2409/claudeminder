import { useState, useEffect, useCallback } from "react";
import { invoke } from "@tauri-apps/api/core";
import { useTranslation } from "react-i18next";
import { isTauri } from "../../utils/mock-data";
import styles from "./command-scheduler.module.css";

type TriggerType = "cron" | "fixed" | "repeated" | "cycle";

interface ScheduledCommand {
  id: string;
  name: string;
  command: string;
  trigger: TriggerType;
  // cron: cron expression
  // fixed: specific time (HH:MM)
  // repeated: interval in minutes
  // cycle: after each reset
  value: string;
  enabled: boolean;
}

interface CommandSchedulerConfig {
  commands: ScheduledCommand[];
}

const defaultCommands: ScheduledCommand[] = [];

export function CommandScheduler() {
  const { t } = useTranslation();
  const [commands, setCommands] = useState<ScheduledCommand[]>(defaultCommands);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [showAddForm, setShowAddForm] = useState(false);

  // New command form state
  const [newCommand, setNewCommand] = useState<Omit<ScheduledCommand, "id">>({
    name: "",
    command: "",
    trigger: "cycle",
    value: "",
    enabled: true,
  });

  useEffect(() => {
    const loadConfig = async () => {
      if (!isTauri()) {
        setLoading(false);
        return;
      }

      try {
        const result = await invoke<{
          config: { scheduler?: CommandSchedulerConfig };
        }>("get_config");
        if (result.config?.scheduler?.commands) {
          setCommands(result.config.scheduler.commands);
        }
      } catch (error) {
        console.error("Failed to load scheduler config:", error);
      } finally {
        setLoading(false);
      }
    };

    loadConfig();
  }, []);

  const saveCommands = useCallback(
    async (updatedCommands: ScheduledCommand[]) => {
      if (!isTauri()) return;

      setSaving(true);
      try {
        await invoke("set_config", {
          configJson: JSON.stringify({
            scheduler: { commands: updatedCommands },
          }),
        });
        setCommands(updatedCommands);
      } catch (error) {
        console.error("Failed to save scheduler config:", error);
      } finally {
        setSaving(false);
      }
    },
    [],
  );

  const handleAddCommand = () => {
    if (!newCommand.name || !newCommand.command) return;

    const id = `cmd_${Date.now()}`;
    const updatedCommands = [...commands, { ...newCommand, id }];
    saveCommands(updatedCommands);
    setNewCommand({
      name: "",
      command: "",
      trigger: "cycle",
      value: "",
      enabled: true,
    });
    setShowAddForm(false);
  };

  const handleDeleteCommand = (id: string) => {
    const updatedCommands = commands.filter((cmd) => cmd.id !== id);
    saveCommands(updatedCommands);
  };

  const handleToggleCommand = (id: string) => {
    const updatedCommands = commands.map((cmd) =>
      cmd.id === id ? { ...cmd, enabled: !cmd.enabled } : cmd,
    );
    saveCommands(updatedCommands);
  };

  const handleUpdateCommand = (
    id: string,
    updates: Partial<ScheduledCommand>,
  ) => {
    const updatedCommands = commands.map((cmd) =>
      cmd.id === id ? { ...cmd, ...updates } : cmd,
    );
    saveCommands(updatedCommands);
    setEditingId(null);
  };

  const getTriggerLabel = (trigger: TriggerType): string => {
    const labels: Record<TriggerType, string> = {
      cron: t("scheduler.triggerCron", "Cron"),
      fixed: t("scheduler.triggerFixed", "Fixed Time"),
      repeated: t("scheduler.triggerRepeated", "Repeated"),
      cycle: t("scheduler.triggerCycle", "On Reset"),
    };
    return labels[trigger];
  };

  const getTriggerPlaceholder = (trigger: TriggerType): string => {
    const placeholders: Record<TriggerType, string> = {
      cron: "0 */5 * * *",
      fixed: "09:00",
      repeated: "30",
      cycle: "",
    };
    return placeholders[trigger];
  };

  const getTriggerHint = (trigger: TriggerType): string => {
    const hints: Record<TriggerType, string> = {
      cron: t(
        "scheduler.hintCron",
        "Cron expression (e.g., '0 */5 * * *' for every 5 hours)",
      ),
      fixed: t("scheduler.hintFixed", "Time in HH:MM format (24-hour)"),
      repeated: t("scheduler.hintRepeated", "Interval in minutes"),
      cycle: t("scheduler.hintCycle", "Runs after each usage reset"),
    };
    return hints[trigger];
  };

  if (loading) {
    return (
      <div className={styles.container}>
        <span className={styles.loadingText}>
          {t("common.loading", "Loading...")}
        </span>
      </div>
    );
  }

  return (
    <div className={styles.container}>
      {/* Commands List */}
      <div className={styles.commandList}>
        {commands.length === 0 && !showAddForm && (
          <div className={styles.emptyState}>
            <span className={styles.emptyText}>
              {t("scheduler.noCommands", "No scheduled commands")}
            </span>
          </div>
        )}

        {commands.map((cmd) => (
          <div
            key={cmd.id}
            className={`${styles.commandItem} ${!cmd.enabled ? styles.disabled : ""}`}
          >
            {editingId === cmd.id ? (
              <div className={styles.editForm}>
                <input
                  type="text"
                  className={styles.input}
                  value={cmd.name}
                  onChange={(e) =>
                    handleUpdateCommand(cmd.id, { name: e.target.value })
                  }
                  placeholder={t("scheduler.namePlaceholder", "Command name")}
                />
                <input
                  type="text"
                  className={styles.input}
                  value={cmd.command}
                  onChange={(e) =>
                    handleUpdateCommand(cmd.id, { command: e.target.value })
                  }
                  placeholder={t(
                    "scheduler.commandPlaceholder",
                    "Shell command",
                  )}
                />
                <select
                  className={styles.select}
                  value={cmd.trigger}
                  onChange={(e) =>
                    handleUpdateCommand(cmd.id, {
                      trigger: e.target.value as TriggerType,
                      value: "",
                    })
                  }
                >
                  <option value="cycle">{getTriggerLabel("cycle")}</option>
                  <option value="repeated">
                    {getTriggerLabel("repeated")}
                  </option>
                  <option value="fixed">{getTriggerLabel("fixed")}</option>
                  <option value="cron">{getTriggerLabel("cron")}</option>
                </select>
                {cmd.trigger !== "cycle" && (
                  <input
                    type="text"
                    className={styles.input}
                    value={cmd.value}
                    onChange={(e) =>
                      handleUpdateCommand(cmd.id, { value: e.target.value })
                    }
                    placeholder={getTriggerPlaceholder(cmd.trigger)}
                  />
                )}
                <button
                  className={styles.doneBtn}
                  onClick={() => setEditingId(null)}
                >
                  {t("common.done", "Done")}
                </button>
              </div>
            ) : (
              <>
                <div className={styles.commandInfo}>
                  <span className={styles.commandName}>{cmd.name}</span>
                  <code className={styles.commandText}>{cmd.command}</code>
                  <span className={styles.triggerBadge}>
                    {getTriggerLabel(cmd.trigger)}
                    {cmd.trigger !== "cycle" && cmd.value && `: ${cmd.value}`}
                  </span>
                </div>
                <div className={styles.commandActions}>
                  <button
                    className={`${styles.toggleBtn} ${cmd.enabled ? styles.active : ""}`}
                    onClick={() => handleToggleCommand(cmd.id)}
                    disabled={saving}
                    title={
                      cmd.enabled
                        ? t("common.disable", "Disable")
                        : t("common.enable", "Enable")
                    }
                  >
                    <span className={styles.toggleThumb} />
                  </button>
                  <button
                    className={styles.editBtn}
                    onClick={() => setEditingId(cmd.id)}
                    title={t("common.edit", "Edit")}
                  >
                    ✎
                  </button>
                  <button
                    className={styles.deleteBtn}
                    onClick={() => handleDeleteCommand(cmd.id)}
                    title={t("common.delete", "Delete")}
                  >
                    ✕
                  </button>
                </div>
              </>
            )}
          </div>
        ))}
      </div>

      {/* Add New Command Form */}
      {showAddForm ? (
        <div className={styles.addForm}>
          <input
            type="text"
            className={styles.input}
            value={newCommand.name}
            onChange={(e) =>
              setNewCommand({ ...newCommand, name: e.target.value })
            }
            placeholder={t("scheduler.namePlaceholder", "Command name")}
          />
          <input
            type="text"
            className={`${styles.input} ${styles.commandInput}`}
            value={newCommand.command}
            onChange={(e) =>
              setNewCommand({ ...newCommand, command: e.target.value })
            }
            placeholder={t(
              "scheduler.commandPlaceholder",
              'Shell command (e.g., claude -p "Start session")',
            )}
          />
          <div className={styles.triggerRow}>
            <select
              className={styles.select}
              value={newCommand.trigger}
              onChange={(e) =>
                setNewCommand({
                  ...newCommand,
                  trigger: e.target.value as TriggerType,
                  value: "",
                })
              }
            >
              <option value="cycle">{getTriggerLabel("cycle")}</option>
              <option value="repeated">{getTriggerLabel("repeated")}</option>
              <option value="fixed">{getTriggerLabel("fixed")}</option>
              <option value="cron">{getTriggerLabel("cron")}</option>
            </select>
            {newCommand.trigger !== "cycle" && (
              <input
                type="text"
                className={styles.input}
                value={newCommand.value}
                onChange={(e) =>
                  setNewCommand({ ...newCommand, value: e.target.value })
                }
                placeholder={getTriggerPlaceholder(newCommand.trigger)}
              />
            )}
          </div>
          <span className={styles.hint}>
            {getTriggerHint(newCommand.trigger)}
          </span>
          <div className={styles.formActions}>
            <button
              className={styles.cancelBtn}
              onClick={() => setShowAddForm(false)}
            >
              {t("common.cancel", "Cancel")}
            </button>
            <button
              className={styles.saveBtn}
              onClick={handleAddCommand}
              disabled={!newCommand.name || !newCommand.command || saving}
            >
              {t("common.add", "Add")}
            </button>
          </div>
        </div>
      ) : (
        <button className={styles.addBtn} onClick={() => setShowAddForm(true)}>
          + {t("scheduler.addCommand", "Add Command")}
        </button>
      )}
    </div>
  );
}

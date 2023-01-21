import gi

from gi.repository import Gtk, Adw, GLib, Pango, Gdk
from datetime import datetime

from iplan.database.database import TasksData, Task, ProjectsData
from iplan.views.project_header import ProjectHeader
from iplan.views.page_item import TaskRow

# Initialize Database connection
tasks_data = TasksData()
projects_data = ProjectsData()

@Gtk.Template(resource_path='/ir/imansalmani/iplan/ui/page/project_list_items.ui')
class ProjectListItems(Gtk.Box):
    __gtype_name__ = "ProjectListItems"
    show_completed_tasks: bool = False
    show_completed_tasks_switch: Gtk.Switch = Gtk.Template.Child()
    scrolled_window: Gtk.ScrolledWindow = Gtk.Template.Child()
    tasks_list: Gtk.ListBox = Gtk.Template.Child()

    def __init__(self) -> None:
        super().__init__()

        drop_target = Gtk.DropTarget.new(TaskRow, Gdk.DragAction.MOVE)
        drop_target.set_preload(True)
        drop_target.connect("drop", self.on_dropped)
        drop_target.connect("motion", self.on_motioned)
        self.tasks_list.add_controller(drop_target)

        self.tasks_list.set_sort_func(self.sort)
        self.connect("map", self.on_mapped)

    # Actions
    def on_mapped(self, *args):
        actions = self.props.root.props.application.actions

        actions["open_project"].connect(
            "activate",
            lambda *args: self.open_project(args[1][1])
        )

        actions["new_task"].connect("activate", self.new)
        actions["refresh_tasks"].connect("activate", self.refresh_tasks)

        actions["toggle_completed_tasks"].connect(
            "change-state",
            lambda *args: self.toggle_completed_tasks(bool(args[1]))
        )

        self.show_completed_tasks_switch.connect(
            "state-set",
            lambda *args: actions["toggle_completed_tasks"].change_state(
                GLib.Variant('b', args[1])
            )
        )

        # open first project
        self.props.root.props.application.project = projects_data.first()
        self.activate_action("app.open_project", GLib.Variant.new_tuple(
            GLib.Variant("b", False),
            GLib.Variant("i", -1)
        ))

    def new(self, *args):
        position = 0
        first_task = self.tasks_list.get_first_child()
        if first_task:
            position = first_task.task.position + 1

        task = tasks_data.add("",self.props.root.props.application.project.id)

        task_ui = TaskRow(task, new=True)
        self.tasks_list.prepend(task_ui)
        task_ui.name_entry.grab_focus()

    def open_project(self, task_id):
        if task_id != -1:
            task = tasks_data.get(task_id)
            if task.done and not self.show_completed_tasks:
                self.props.root.props.application.actions["toggle_completed_tasks"].change_state(
                    GLib.Variant('b', True)
                )

        self.timer_running = False
        self.clear()
        self.fetch()

        self.show_completed_tasks_switch.set_state(False)

        if task_id != -1:
            tasks_ui = list(self.tasks_list.observe_children())
            searched_task_ui = None
            for task_ui in tasks_ui:
                if task_ui.task.id == task_id:
                    searched_task_ui = task_ui
                    break
            GLib.idle_add(lambda *args: self.props.root.set_focus(searched_task_ui))

    def toggle_completed_tasks(self, state):
        self.show_completed_tasks = state
        self.clear()
        self.fetch()

    def refresh_tasks(self, *args):
        self.clear()
        self.fetch()

    # UI
    def on_dropped(
            self,
            target: Gtk.DropTarget,
            source_widget: TaskRow,
            x: float, y: float) -> bool:
        target_widget: TaskRow = self.tasks_list.get_row_at_y(y)

        source_position = source_widget.task.position
        target_position = target_widget.task.position

        if source_position == target_position:
            return False

        source_widget.task.position = target_position
        tasks_data.update(source_widget.task)

        target_widget.task.position = source_position
        tasks_data.update(target_widget.task)

        self.tasks_list.invalidate_sort()
        return True

    def on_motioned(self, target: Gtk.DropTarget, x, y):
        target_widget: TaskRow = self.tasks_list.get_row_at_y(y)
        source_widget: TaskRow = target.get_value()

        if source_widget == target_widget:
            return 0

        scrolled_window_height = self.scrolled_window.get_size(Gtk.Orientation.VERTICAL)
        tasks_list_height = self.tasks_list.get_size(Gtk.Orientation.VERTICAL)

        if tasks_list_height > scrolled_window_height:
            adjustment = self.scrolled_window.props.vadjustment
            step = adjustment.get_step_increment() / 3
            v_pos = adjustment.get_value()
            if y - v_pos > 475:
                adjustment.set_value(v_pos + step)
            elif y - v_pos < 25:
                adjustment.set_value(v_pos - step)

        return Gdk.DragAction.MOVE

    def sort(
            self,
            row1: Gtk.ListBoxRow,
            row2: Gtk.ListBoxRow) -> int:
        return row2.task.position - row1.task.position

    def fetch(self):
        tasks = tasks_data.all(
            show_completed_tasks=self.show_completed_tasks,
            project=self.props.root.props.application.project
        )
        for task in tasks:
            task_ui = TaskRow(task)
            self.tasks_list.append(task_ui)

    def clear(self):
        while True:
            row = self.tasks_list.get_first_child()
            if row:
                self.tasks_list.remove(row)
            else:
                break

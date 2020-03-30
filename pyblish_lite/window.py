"""Main Window

States:
    These are all possible states and their transitions.


      reset
        '
        '
        '
     ___v__
    |      |       reset
    | Idle |--------------------.
    |      |<-------------------'
    |      |
    |      |                   _____________
    |      |     validate     |             |    reset     # TODO
    |      |----------------->| In-progress |-----------.
    |      |                  |_____________|           '
    |      |<-------------------------------------------'
    |      |
    |      |                   _____________
    |      |      publish     |             |
    |      |----------------->| In-progress |---.
    |      |                  |_____________|   '
    |      |<-----------------------------------'
    |______|


Todo:
    There are notes spread throughout this project with the syntax:

    - TODO(username)

    The `username` is a quick and dirty indicator of who made the note
    and is by no means exclusive to that person in terms of seeing it
    done. Feel free to do, or make your own TODO's as you code. Just
    make sure the description is sufficient for anyone reading it for
    the first time to understand how to actually to it!

"""
from functools import partial

from . import delegate, model, settings, util, view, tree
from .awesome import tags as awesome

from .vendor.Qt import QtCore, QtGui, QtWidgets


class Window(QtWidgets.QDialog):
    def __init__(self, controller, parent=None):
        super(Window, self).__init__(parent)
        icon = QtGui.QIcon(util.get_asset("img", "logo-extrasmall.png"))
        if parent is None:
            on_top_flag = QtCore.Qt.WindowStaysOnTopHint
        else:
            on_top_flag = QtCore.Qt.Dialog

        self.setWindowFlags(
            self.windowFlags() |
            QtCore.Qt.WindowTitleHint |
            QtCore.Qt.WindowMaximizeButtonHint |
            QtCore.Qt.WindowMinimizeButtonHint |
            QtCore.Qt.WindowCloseButtonHint |
            on_top_flag
        )
        self.setWindowIcon(icon)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)

        self.controller = controller

        """General layout
         __________________       _____________________
        |                  |     |       |       |     |
        |      Header      | --> | Tab   | Tab   | Tab |
        |__________________|     |_______|_______|_____|
        |                  |      _____________________
        |                  |     |                     |
        |                  |     |                     |
        |       Body       |     |                     |
        |                  | --> |        Page         |
        |                  |     |                     |
        |                  |     |_____________________|
        |__________________|      _____________________
        |                  |     |           |         |
        |      Footer      |     | Status    | Buttons |
        |__________________|     |___________|_________|

        """

        header = QtWidgets.QWidget()
        layout = QtWidgets.QHBoxLayout(header)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        tab_widget = QtWidgets.QWidget()
        artist_tab = QtWidgets.QRadioButton()
        overview_tab = QtWidgets.QRadioButton()
        terminal_tab = QtWidgets.QRadioButton()
        spacer = QtWidgets.QWidget()

        aditional_btns = QtWidgets.QWidget()

        aditional_btns_layout = QtWidgets.QHBoxLayout(aditional_btns)

        presets_button = view.ButtonWithMenu(awesome["filter"])
        presets_button.setEnabled(False)
        aditional_btns_layout.addWidget(presets_button)

        layout_tab = QtWidgets.QHBoxLayout(tab_widget)
        layout_tab.setContentsMargins(0, 0, 0, 0)
        layout_tab.setSpacing(0)
        layout_tab.addWidget(artist_tab, 0)
        layout_tab.addWidget(overview_tab, 0)
        layout_tab.addWidget(terminal_tab, 0)
        layout_tab.addWidget(spacer, 1)  # Compress items to the left
        layout_tab.addWidget(aditional_btns, 1)

        layout.addWidget(tab_widget)

        """Artist Page
         __________________
        |                  |
        | | ------------   |
        | | -----          |
        |                  |
        | | --------       |
        | | -------        |
        |                  |
        |__________________|

        """

        artist_page = QtWidgets.QWidget()

        artist_view = view.Item()
        artist_view.show_perspective.connect(self.toggle_perspective_widget)

        artist_delegate = delegate.Artist()
        artist_view.setItemDelegate(artist_delegate)

        layout = QtWidgets.QVBoxLayout(artist_page)
        layout.addWidget(artist_view)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(0)

        """Overview Page
         ___________________
        |                  |
        | o ----- o----    |
        | o ----  o---     |
        | o ----  o----    |
        | o ----  o------  |
        |                  |
        |__________________|

        """

        overview_page = QtWidgets.QWidget()

        left_view = tree.View()
        right_view = tree.View()

        item_delegate = delegate.ItemAndSection()
        left_view.setItemDelegate(item_delegate)
        right_view.setItemDelegate(item_delegate)

        layout = QtWidgets.QHBoxLayout(overview_page)
        layout.addWidget(left_view, 1)
        layout.addWidget(right_view, 1)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(0)

        """Terminal

         __________________
        |                  |
        |  \               |
        |   \              |
        |   /              |
        |  /  ______       |
        |                  |
        |__________________|

        """

        terminal_container = QtWidgets.QWidget()

        terminal_delegate = delegate.LogsAndDetails()
        terminal_view = view.TerminalView()
        terminal_view.setItemDelegate(terminal_delegate)

        terminal_model = model.Terminal()

        terminal_proxy = model.TerminalProxy()
        terminal_proxy.setSourceModel(terminal_model)

        terminal_view.setModel(terminal_proxy)

        layout = QtWidgets.QVBoxLayout(terminal_container)
        layout.addWidget(terminal_view)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(0)

        terminal_footer = QtWidgets.QWidget()

        search_box = QtWidgets.QLineEdit()
        instance_combo = QtWidgets.QComboBox()
        plugin_combo = QtWidgets.QComboBox()
        show_errors = QtWidgets.QCheckBox()
        show_records = QtWidgets.QCheckBox()
        show_debug = QtWidgets.QCheckBox()
        show_info = QtWidgets.QCheckBox()
        show_warning = QtWidgets.QCheckBox()
        show_error = QtWidgets.QCheckBox()
        show_critical = QtWidgets.QCheckBox()

        plugin_combo.setProperty("combolist", True)
        instance_combo.setProperty("combolist", True)

        layout = QtWidgets.QHBoxLayout(terminal_footer)
        for w in (
            search_box,
            instance_combo,
            plugin_combo,
            show_errors,
            show_records,
            show_debug,
            show_info,
            show_warning,
            show_error,
            show_critical
        ):
            layout.addWidget(w)

        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(3)

        terminal_page = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(terminal_page)
        layout.addWidget(terminal_container)
        # layout.addWidget(terminal_footer)  # TODO
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Add some room between window borders and contents
        body = QtWidgets.QWidget()
        layout = QtWidgets.QHBoxLayout(body)
        layout.setContentsMargins(5, 5, 5, 1)
        layout.addWidget(artist_page)
        layout.addWidget(overview_page)
        layout.addWidget(terminal_page)

        """Comment Box
         ____________________________ ______________
        |> My comment                | intent [ v ] |
        |                            |              |
        |____________________________|______________|

        """

        comment_box = view.CommentBox("Comment...", self)

        intent_box = QtWidgets.QComboBox()

        intent_model = model.IntentModel()
        intent_box.setModel(intent_model)
        intent_box.currentIndexChanged.connect(self.on_intent_changed)

        comment_intent_widget = QtWidgets.QWidget()
        comment_intent_layout = QtWidgets.QHBoxLayout(comment_intent_widget)
        comment_intent_layout.setContentsMargins(0, 0, 0, 0)
        comment_intent_layout.setSpacing(5)
        comment_intent_layout.addWidget(comment_box)
        comment_intent_layout.addWidget(intent_box)

        """Details View
         ____________________________
        |                            |
        | An Item              23 ms |
        | - family                   |
        |                            |
        |----------------------------|
        |                            |
        | Docstring                  |
        |____________________________|

        """

        details = view.Details(self)

        """Footer
         ______________________
        |             ___  ___ |
        |            | o || > ||
        |            |___||___||
        |______________________|

        """

        footer = QtWidgets.QWidget()
        info = QtWidgets.QLabel(footer)
        spacer = QtWidgets.QWidget(footer)
        reset = QtWidgets.QPushButton(awesome["refresh"], footer)
        validate = QtWidgets.QPushButton(awesome["flask"], footer)
        play = QtWidgets.QPushButton(awesome["play"], footer)
        stop = QtWidgets.QPushButton(awesome["stop"], footer)

        layout = QtWidgets.QHBoxLayout()
        layout.setContentsMargins(5, 5, 5, 5)
        layout.addWidget(info, 0)
        layout.addWidget(spacer, 1)
        layout.addWidget(stop, 0)
        layout.addWidget(reset, 0)
        layout.addWidget(validate, 0)
        layout.addWidget(play, 0)

        footer_layout = QtWidgets.QVBoxLayout(footer)
        footer_layout.addWidget(comment_intent_widget)
        footer_layout.addLayout(layout)

        footer.setProperty("success", -1)

        # Placeholder for when GUI is closing
        # TODO(marcus): Fade to black and the the user about what's happening
        closing_placeholder = QtWidgets.QWidget(self)
        closing_placeholder.setSizePolicy(QtWidgets.QSizePolicy.Expanding,
                                          QtWidgets.QSizePolicy.Expanding)
        closing_placeholder.hide()

        self.last_persp_index = None
        self.perspective_widget = view.PerspectiveWidget(self)
        self.perspective_widget.hide()

        # Main layout
        self.main_widget = QtWidgets.QWidget(self)
        layout = QtWidgets.QVBoxLayout(self.main_widget)
        layout.addWidget(header, 0)
        layout.addWidget(body, 3)
        layout.addWidget(self.perspective_widget, 3)
        layout.addWidget(closing_placeholder, 1)
        layout.addWidget(footer, 0)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        self.main_widget.setLayout(layout)

        self.main_layout = QtWidgets.QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        self.main_layout.addWidget(self.main_widget)
        """Animation
           ___
          /   \
         |     |            ___
          \___/            /   \
                   ___    |     |
                  /   \    \___/
                 |     |
                  \___/

        """

        # Display info
        info_effect = QtWidgets.QGraphicsOpacityEffect(info)
        info.setGraphicsEffect(info_effect)

        timeline = QtCore.QSequentialAnimationGroup()

        on = QtCore.QPropertyAnimation(info_effect, b"opacity")
        on.setDuration(0)
        on.setStartValue(0)
        on.setEndValue(1)

        off = QtCore.QPropertyAnimation(info_effect, b"opacity")
        off.setDuration(0)
        off.setStartValue(1)
        off.setEndValue(0)

        fade = QtCore.QPropertyAnimation(info_effect, b"opacity")
        fade.setDuration(500)
        fade.setStartValue(1.0)
        fade.setEndValue(0.0)

        timeline.addAnimation(on)
        timeline.addPause(50)
        timeline.addAnimation(off)
        timeline.addPause(50)
        timeline.addAnimation(on)
        timeline.addPause(2000)
        timeline.addAnimation(fade)

        info_animation = timeline

        """Setup

        Widgets are referred to in CSS via their object-name. We
        use the same mechanism internally to refer to objects; so rather
        than storing widgets as self.my_widget, it is referred to as:

        >>> my_widget = self.findChild(QtWidgets.QWidget, "MyWidget")

        This way there is only ever a single method of referring to any widget.

              ___
             |   |
          /\/     \/\
         /     _     \
         \    / \    /
          |   | |   |
         /    \_/    \
         \           /
          \/\     /\/
             |___|

        """

        instance_model = model.Instance()
        plugin_model = model.Plugin()

        filter_model = model.ProxyModel(plugin_model)

        artist_view.setModel(instance_model)

        left_proxy = tree.FamilyGroupProxy()
        left_proxy.setSourceModel(instance_model)
        left_proxy.set_group_role(model.Families)
        left_view.setModel(left_proxy)

        right_proxy = tree.PluginOrderGroupProxy()
        right_proxy.setSourceModel(plugin_model)
        right_proxy.set_group_role(model.Order)
        right_view.setModel(right_proxy)

        instance_combo.setModel(instance_model)
        plugin_combo.setModel(plugin_model)

        names = {
            # Main
            "Header": header,
            "Body": body,
            "Footer": footer,

            # Modals
            "Details": details,

            # Pages
            "Artist": artist_page,
            "Overview": overview_page,
            "Terminal": terminal_page,

            # Tabs
            "ArtistTab": artist_tab,
            "OverviewTab": overview_tab,
            "TerminalTab": terminal_tab,

            # Buttons
            "Play": play,
            "Validate": validate,
            "Reset": reset,
            "Stop": stop,

            # Misc
            "FooterSpacer": spacer,
            "FooterInfo": info,
            "CommentIntentWidget": comment_intent_widget,
            "CommentBox": comment_box,
            "CommentPlaceholder": comment_box.placeholder,
            "ClosingPlaceholder": closing_placeholder,
            "IntentBox": intent_box
        }

        for name, w in names.items():
            w.setObjectName(name)

        # Enable CSS on plain QWidget objects
        for w in (header,
                  body,
                  artist_page,
                  comment_box,
                  overview_page,
                  terminal_page,
                  footer,
                  play,
                  validate,
                  stop,
                  details,
                  reset,
                  closing_placeholder):
            w.setAttribute(QtCore.Qt.WA_StyledBackground)

        self.data = {
            "header": header,
            "body": body,
            "footer": footer,
            "views": {
                "artist": artist_view,
                "left": left_view,
                "right": right_view,
                "terminal": terminal_view,
            },
            "modals": {
                "details": details
            },
            "proxies": {
                "plugins": right_proxy,
                "instances": left_proxy,
                "terminal": terminal_proxy
            },
            "models": {
                "instances": instance_model,
                "plugins": plugin_model,
                "filter": filter_model,
                "terminal": terminal_model,
                "intent_model": intent_model
            },
            "terminal_toggles": {
                "record": show_records,
                "debug": show_debug,
                "info": show_info,
                "warning": show_warning,
                "error": show_error,
                "critical": show_critical
            },
            "tabs": {
                "artist": artist_tab,
                "overview": overview_tab,
                "terminal": terminal_tab,
                "current": "artist"
            },
            "pages": {
                "artist": artist_page,
                "overview": overview_page,
                "terminal": terminal_page,
            },
            "comment_intent": {
                "comment_intent": comment_intent_widget,
                "comment": comment_box,
                "intent": intent_box
            },
            "buttons": {
                "play": play,
                "validate": validate,
                "stop": stop,
                "reset": reset
            },
            "aditional_btns": {
                "presets_button": presets_button
            },
            "animation": {
                "display_info": info_animation,
            },

            "state": {
                "is_closing": False,
            }
        }

        # Pressing Enter defaults to Play
        play.setFocus()

        """Signals
         ________     ________
        |________|-->|________|
                         |
                         |
                      ___v____
                     |________|

        """

        artist_tab.toggled.connect(
            lambda: self.on_tab_changed("artist"))
        overview_tab.toggled.connect(
            lambda: self.on_tab_changed("overview"))
        terminal_tab.toggled.connect(
            lambda: self.on_tab_changed("terminal"))

        left_view.show_perspective.connect(self.toggle_perspective_widget)
        right_view.show_perspective.connect(self.toggle_perspective_widget)

        controller.was_reset.connect(self.on_was_reset)
        controller.was_validated.connect(self.on_was_validated)
        controller.was_published.connect(self.on_was_published)
        controller.was_acted.connect(self.on_was_acted)
        controller.was_finished.connect(self.on_finished)

        controller.was_reset.connect(left_proxy.rebuild)
        controller.was_validated.connect(left_proxy.rebuild)
        controller.was_published.connect(left_proxy.rebuild)
        controller.was_acted.connect(left_proxy.rebuild)
        controller.was_finished.connect(left_proxy.rebuild)

        controller.was_reset.connect(left_view.expandAll)
        controller.was_validated.connect(left_view.expandAll)
        controller.was_published.connect(left_view.expandAll)
        controller.was_acted.connect(left_view.expandAll)
        controller.was_finished.connect(left_view.expandAll)

        # Discovery happens synchronously during reset, that's
        # why it's important that this connection is triggered
        # right away.
        controller.was_discovered.connect(self.on_was_discovered,
                                          QtCore.Qt.DirectConnection)

        # This is called synchronously on each process
        controller.was_processed.connect(self.on_was_processed,
                                         QtCore.Qt.DirectConnection)

        # NOTE: Listeners to this signal are run in the main thread
        controller.about_to_process.connect(self.on_about_to_process,
                                            QtCore.Qt.DirectConnection)

        artist_view.toggled.connect(self.on_item_toggled)
        left_view.toggled.connect(self.on_item_toggled)
        right_view.toggled.connect(self.on_item_toggled)

        reset.clicked.connect(self.on_reset_clicked)
        validate.clicked.connect(self.on_validate_clicked)
        play.clicked.connect(self.on_play_clicked)
        stop.clicked.connect(self.on_stop_clicked)
        comment_box.textChanged.connect(self.on_comment_entered)
        comment_box.returnPressed.connect(self.on_play_clicked)
        right_view.customContextMenuRequested.connect(
            self.on_plugin_action_menu_requested)

        for box in (show_errors,
                    show_records,
                    show_debug,
                    show_info,
                    show_warning,
                    show_error,
                    show_critical):
            box.setChecked(True)

        self.data["tabs"][settings.InitialTab].setChecked(True)

    # -------------------------------------------------------------------------
    #
    # Event handlers
    #
    # -------------------------------------------------------------------------
    def set_presets(self, key):
        plugin_settings = self.controller.possible_presets.get(key)
        plugin_model = self.data["models"]["plugins"]

        for plugin in plugin_model.items:
            if not plugin.optional:
                continue

            value = plugin_settings.get(
                plugin.__name__,
                # if plugin is not in presets then set default value
                self.controller.optional_default.get(plugin.__name__)
            )
            if value is None:
                continue

            index = plugin_model.items.index(plugin)
            index = plugin_model.createIndex(index, 0)

            plugin_model.setData(index, value, model.IsChecked)

        self.data["proxies"]["plugins"].layoutChanged.emit()

    def toggle_perspective_widget(self, index=None):
        show = False
        self.last_persp_index = None
        if index:
            show = True
            self.last_persp_index = index
            self.perspective_widget.set_context(index)

        self.data['body'].setVisible(not show)
        self.data['header'].setVisible(not show)

        self.perspective_widget.setVisible(show)

    def on_item_expanded(self, index, state):
        if not index.data(model.IsExpandable):
            return

        if state is None:
            state = not index.data(model.Expanded)

        # Collapse others
        for i in index.model():
            index.model().setData(i, False, model.Expanded)

        index.model().setData(index, state, model.Expanded)

    def on_item_toggled(self, index, state=None):
        """An item is requesting to be toggled"""
        if not index.data(model.IsIdle):
            return self.info("Cannot toggle")

        if not index.data(model.IsOptional):
            return self.info("This item is mandatory")

        if state is None:
            state = not index.data(model.IsChecked)

        index.model().setData(index, state, model.IsChecked)

        # Withdraw option to publish if no instances are toggled

        any_instances = any(
            index.data(model.IsChecked)
            for index in self.data["models"]["instances"]
        )

        buttons = self.data["buttons"]
        buttons["play"].setEnabled(
            buttons["play"].isEnabled() and any_instances
        )
        buttons["validate"].setEnabled(
            buttons["validate"].isEnabled() and any_instances
        )

        # Emit signals
        if index.data(model.Type) == "instance":
            util.defer(100, lambda: self.controller.emit_(
                signal="instanceToggled",
                kwargs={
                    "new_value": state,
                    "old_value": not state,
                    "instance": index.data(model.Object)
                }
            ))
            self.update_compatibility()

        if index.data(model.Type) == "plugin":
            util.defer(100, lambda: self.controller.emit_(
                signal="pluginToggled",
                kwargs={
                    "new_value": state,
                    "old_value": not state,
                    "plugin": index.data(model.Object)
                }
            ))

    def on_tab_changed(self, target):
        for page in self.data["pages"].values():
            page.hide()

        page = self.data["pages"][target]

        comment_intent = self.data["comment_intent"]["comment_intent"]
        if target == "terminal":
            comment_intent.setVisible(False)
        else:
            comment_intent.setVisible(True)

        page.show()

        self.data["tabs"]["current"] = target

    def on_validate_clicked(self):
        comment_box = self.data["comment_intent"]["comment"]
        intent_box = self.data["comment_intent"]["intent"]

        comment_box.setEnabled(False)
        intent_box.setEnabled(False)

        self.validate()

    def on_play_clicked(self):
        comment_box = self.data["comment_intent"]["comment"]
        intent_box = self.data["comment_intent"]["intent"]

        comment_box.setEnabled(False)
        intent_box.setEnabled(False)

        self.publish()

    def on_reset_clicked(self):
        self.reset()

    def on_stop_clicked(self):
        self.info("Stopping..")
        self.controller.is_running = False

        buttons = self.data["buttons"]
        buttons["reset"].setEnabled(True)
        buttons["play"].setEnabled(False)
        buttons["stop"].setEnabled(False)

        self.on_finished()

    def on_comment_entered(self):
        """The user has typed a comment"""
        text_edit = self.data["comment_intent"]["comment"]
        comment = text_edit.text()

        # Store within context
        context = self.controller.context
        context.data["comment"] = comment

    def on_intent_changed(self):
        intent_box = self.data["comment_intent"]["intent"]
        idx = intent_box.model().index(intent_box.currentIndex(), 0)
        intent_value = intent_box.model().data(idx, model.IntentItemValue)
        intent_label = intent_box.model().data(idx, QtCore.Qt.DisplayRole)

        self.controller.context.data["intent"] = {
            "value": intent_value,
            "label": intent_label
        }

    def on_about_to_process(self, plugin, instance):
        """Reflect currently running pair in GUI"""

        if instance is not None:
            instance_model = self.data["models"]["instances"]
            index = instance_model.items.index(instance)
            index = instance_model.createIndex(index, 0)
            instance_model.setData(index, True, model.IsProcessing)
            # emit layoutChanged to update GUI
            instance_proxies = self.data["proxies"]["instances"]
            instance_proxies.layoutChanged.emit()

        buttons = self.data["buttons"]
        if buttons["play"].isEnabled():
            buttons["play"].setEnabled(False)

        if buttons["validate"].isEnabled():
            buttons["validate"].setEnabled(False)

        if buttons["reset"].isEnabled():
            buttons["reset"].setEnabled(False)

        if not buttons["reset"].isEnabled():
            buttons["stop"].setEnabled(True)

        plugin_model = self.data["models"]["plugins"]
        index = plugin_model.items.index(plugin)
        index = plugin_model.createIndex(index, 0)

        plugin_model.setData(index, True, model.IsProcessing)

        # emit layoutChanged to update GUI
        plugin_proxies = self.data["proxies"]["plugins"]
        plugin_proxies.layoutChanged.emit()

        self.info("{} {}".format(
            self.tr("Processing"), index.data(QtCore.Qt.DisplayRole)
        ))

    def on_plugin_action_menu_requested(self, pos):
        """The user right-clicked on a plug-in
         __________
        |          |
        | Action 1 |
        | Action 2 |
        | Action 3 |
        |          |
        |__________|

        """

        index = self.data["views"]["right"].indexAt(pos)
        actions = index.data(model.Actions)

        if not actions:
            return

        menu = QtWidgets.QMenu(self)
        plugins_index = self.data["proxies"]["plugins"].mapToSource(index)
        plugin = self.data["models"]["plugins"].items[plugins_index.row()]
        print("plugin is: %s" % plugin)

        for action in actions:
            qaction = QtWidgets.QAction(action.label or action.__name__, self)
            qaction.triggered.connect(partial(self.act, plugin, action))
            menu.addAction(qaction)

        menu.popup(self.data["views"]["right"].viewport().mapToGlobal(pos))

    def on_was_discovered(self):
        models = self.data["models"]
        for key, value in self.controller.plugins.items():
            for plugin in value:
                models["plugins"].append(plugin)

    def update_compatibility(self):
        models = self.data["models"]
        proxies = self.data["proxies"]

        instances = models["instances"].items
        models["plugins"].update_compatibility(
            self.controller.context, instances
        )
        proxies["plugins"].rebuild()

        right_view = self.data['views']['right']
        right_view_model = right_view.model()
        for child in right_view_model.root.children():
            child_idx = right_view_model.createIndex(child.row(), 0, child)
            right_view.expand(child_idx)
            any_failed = False
            all_succeeded = True
            for plugin_item in child.children():
                if plugin_item.data(model.IsOptional):
                    if not plugin_item.data(model.IsChecked):
                        continue
                if plugin_item.data(model.HasFailed):
                    any_failed = True
                    break
                if not plugin_item.data(model.HasSucceeded):
                    all_succeeded = False
                    break

            if all_succeeded and not any_failed:
                right_view.collapse(child_idx)

    def on_was_reset(self):
        models = self.data["models"]

        self.info(self.tr("Finishing up reset.."))

        items = [models["instances"].context_item]
        items.extend([instance for instance in self.controller.context])

        models["instances"].reset()
        for item in items:
            # Set processed, succeeded and idle back to default stage after
            # collecting
            item._is_idle = True
            item._has_succeeded = False
            item._has_processed = False
            models["instances"].append(item)

        failed = False
        for index in self.data["models"]["plugins"]:
            if index.data(model.HasFailed):
                failed = True
                break

        buttons = self.data["buttons"]
        buttons["play"].setEnabled(not failed)
        buttons["validate"].setEnabled(not failed)
        buttons["reset"].setEnabled(True)
        buttons["stop"].setEnabled(False)

        aditional_btns = self.data["aditional_btns"]
        aditional_btns["presets_button"].clearMenu()
        if self.controller.possible_presets:
            aditional_btns["presets_button"].setEnabled(True)
            for key in self.controller.possible_presets:
                aditional_btns["presets_button"].addItem(
                    key, partial(self.set_presets, key)
                )

        models["instances"].restore_checkstate()
        models["plugins"].restore_checkstate()

        # Append placeholder comment from Context
        # This allows users to inject a comment from elsewhere,
        # or to perhaps provide a placeholder comment/template
        # for artists to fill in.
        comment = self.controller.context.data.get("comment")
        comment_box = self.data["comment_intent"]["comment"]
        comment_box.setText(comment or None)
        comment_box.setEnabled(True)

        intent_box = self.data["comment_intent"]["intent"]
        intent_model = intent_box.model()
        if intent_model.has_items:
            self.on_intent_changed()
        intent_box.setEnabled(True)

        # Refresh tab
        self.on_tab_changed(self.data["tabs"]["current"])

    def on_was_validated(self):
        plugin_model = self.data["models"]["plugins"]
        instance_model = self.data["models"]["instances"]

        failed = False
        for index in plugin_model:
            index.model().setData(index, False, model.IsIdle)
            if failed:
                continue
            if index.data(model.HasFailed):
                failed = True

        for index in instance_model:
            if (
                not index.data(model.HasFailed) and
                not index.data(model.HasSucceeded)
            ):
                index.model().setData(index, True, model.HasSucceeded)

            index.model().setData(index, False, model.IsIdle)

        buttons = self.data["buttons"]
        buttons["play"].setEnabled(not failed)
        buttons["validate"].setEnabled(False)
        buttons["reset"].setEnabled(True)
        buttons["stop"].setEnabled(False)

    def on_was_published(self):
        plugin_model = self.data["models"]["plugins"]
        instance_model = self.data["models"]["instances"]

        for index in plugin_model:
            index.model().setData(index, False, model.IsIdle)

        for index in instance_model:
            index.model().setData(index, False, model.IsIdle)

        buttons = self.data["buttons"]
        buttons["play"].setEnabled(False)
        buttons["validate"].setEnabled(False)
        buttons["reset"].setEnabled(True)
        buttons["stop"].setEnabled(False)

        if self.controller.current_error is None:
            self.data["footer"].setProperty("success", 1)
            self.data["footer"].style().polish(self.data["footer"])

    def on_was_processed(self, result):
        models = self.data["models"]

        for instance in self.controller.context:
            if instance.id not in models["instances"].ids:
                models["instances"].append(instance)

            family = instance.data["family"]
            if family:
                plugins_filter = self.data["models"]["filter"]
                plugins_filter.add_inclusion(role="families", value=family)

            families = instance.data.get("families")
            if families:
                for f in families:
                    plugins_filter = self.data["models"]["filter"]
                    plugins_filter.add_inclusion(role="families", value=f)

        error = result.get('error')
        if error:
            records = result.get('records') or []
            fname, line_no, func, exc = error.traceback

            records.append({
                'label': str(error),
                'type': 'error',
                'filename': str(fname),
                'lineno': str(line_no),
                'func': str(func),
                'traceback': error.formatted_traceback,
            })

            result['records'] = records

            # Toggle from artist to overview tab on error
            if self.data["tabs"]["artist"].isChecked():
                self.data["tabs"]["overview"].toggle()

        models["plugins"].update_with_result(result)
        models["instances"].update_with_result(result)
        models["terminal"].update_with_result(result)

        self.data['proxies']['terminal'].rebuild()

        if self.last_persp_index:
            self.perspective_widget.set_context(self.last_persp_index)

    def on_was_acted(self, result):
        buttons = self.data["buttons"]
        buttons["reset"].setEnabled(True)
        buttons["stop"].setEnabled(False)

        # Update action with result
        model_ = self.data["models"]["plugins"]

        index = model_.items.index(result["plugin"])
        index = model_.createIndex(index, 0)

        model_.setData(index, not result["success"], model.ActionFailed)
        model_.setData(index, False, model.IsProcessing)

        models = self.data["models"]

        error = result.get('error')
        if error:
            records = result.get('records') or []
            fname, line_no, func, exc = error.traceback

            records.append({
                'label': str(error),
                'type': 'error',
                'filename': str(fname),
                'lineno': str(line_no),
                'func': str(func),
                'traceback': error.formatted_traceback
            })

            result['records'] = records

        models["plugins"].update_with_result(result)
        models["instances"].update_with_result(result)
        models["terminal"].update_with_result(result)

        self.on_finished()

    def on_finished(self):
        """Finished signal handler"""
        self.controller.is_running = False

        error = self.controller.current_error
        if error is not None:
            self.info(self.tr("Stopped due to error(s), see Terminal."))
            self.data["footer"].setProperty("success", 0)
            self.data["footer"].style().polish(self.data["footer"])
            comment_box = self.data["comment_intent"]["comment"]
            comment_box.setEnabled(False)
            intent_box = self.data["comment_intent"]["intent"]
            intent_box.setEnabled(False)

        else:
            self.info(self.tr("Finished successfully!"))

        self.update_compatibility()
    # -------------------------------------------------------------------------
    #
    # Functions
    #
    # -------------------------------------------------------------------------

    def reset(self):
        """Prepare GUI for reset"""
        self.info(self.tr("About to reset.."))

        self.data["aditional_btns"]["presets_button"].setEnabled(False)
        self.data["footer"].setProperty("success", -1)
        self.data["footer"].style().polish(self.data["footer"])

        models = self.data["models"]

        models["instances"].store_checkstate()
        models["plugins"].store_checkstate()

        # Reset current ids to secure no previous instances get mixed in.
        models["instances"].ids = []

        for model in models.values():
            model.reset()

        for button in self.data["buttons"].values():
            button.setEnabled(False)

        intent_box = self.data["comment_intent"]["intent"]
        intent_model = intent_box.model()
        intent_box.setVisible(intent_model.has_items)
        if intent_model.has_items:
            intent_box.setCurrentIndex(intent_model.default_index)

        # Prepare Context object in controller (create new one)
        self.controller.prepare_for_reset()
        # Append context object to instances model
        self.data["models"]["instances"].append(self.controller.context)
        # Launch controller reset
        util.defer(500, self.controller.reset)

    def validate(self):
        self.info(self.tr("Preparing validate.."))
        for button in self.data["buttons"].values():
            button.setEnabled(False)

        self.data["buttons"]["stop"].setEnabled(True)
        util.defer(5, self.controller.validate)

    def publish(self):
        self.info(self.tr("Preparing publish.."))

        for button in self.data["buttons"].values():
            button.setEnabled(False)

        self.data["buttons"]["stop"].setEnabled(True)
        util.defer(5, self.controller.publish)

    def act(self, plugin, action):
        self.info("%s %s.." % (self.tr("Preparing"), action))

        for button in self.data["buttons"].values():
            button.setEnabled(False)

        self.data["buttons"]["stop"].setEnabled(True)
        self.controller.is_running = True

        # Cause view to update, but it won't visually
        # happen until Qt is given time to idle..
        model_ = self.data["models"]["plugins"]

        index = model_.items.index(plugin)
        index = model_.createIndex(index, 0)

        for key, value in {
            model.ActionIdle: False,
            model.ActionFailed: False,
            model.IsProcessing: True
        }.items():
            model_.setData(index, value, key)

        # Give Qt time to draw
        util.defer(100, lambda: self.controller.act(plugin, action))

        self.info(self.tr("Action prepared."))

    def closeEvent(self, event):
        """Perform post-flight checks before closing

        Make sure processing of any kind is wrapped up before closing

        """

        # Make it snappy, but take care to clean it all up.
        # TODO(marcus): Enable GUI to return on problem, such
        # as asking whether or not the user really wants to quit
        # given there are things currently running.
        self.hide()

        if self.data["state"]["is_closing"]:

            # Explicitly clear potentially referenced data
            self.info(self.tr("Cleaning up models.."))
            for view in self.data["views"].values():
                view.model().deleteLater()
                view.setModel(None)

            self.info(self.tr("Cleaning up terminal.."))
            for item in self.data["models"]["terminal"].items:
                del(item)

            self.info(self.tr("Cleaning up controller.."))
            self.controller.cleanup()

            self.info(self.tr("All clean!"))
            self.info(self.tr("Good bye"))
            return super(Window, self).closeEvent(event)

        self.info(self.tr("Closing.."))

        def on_problem():
            self.heads_up("Warning", "Had trouble closing down. "
                          "Please tell someone and try again.")
            self.show()

        if self.controller.is_running:
            self.info(self.tr("..as soon as processing is finished.."))
            self.controller.is_running = False
            self.finished.connect(self.close)
            util.defer(2000, on_problem)
            return event.ignore()

        self.data["state"]["is_closing"] = True

        util.defer(200, self.close)
        return event.ignore()

    def reject(self):
        """Handle ESC key"""

        if self.controller.is_running:
            self.info(self.tr("Stopping.."))
            self.controller.is_running = False

    # -------------------------------------------------------------------------
    #
    # Feedback
    #
    # -------------------------------------------------------------------------

    def info(self, message):
        """Print user-facing information

        Arguments:
            message (str): Text message for the user

        """

        info = self.findChild(QtWidgets.QLabel, "FooterInfo")
        info.setText(message)

        # Include message in terminal
        self.data["models"]["terminal"].append({
            "label": message,
            "type": "info"
        })

        animation = self.data["animation"]["display_info"]
        animation.stop()
        animation.start()

        # TODO(marcus): Should this be configurable? Do we want
        # the shell to fill up with these messages?
        util.u_print(message)

    def warning(self, message):
        """Block processing and print warning until user hits "Continue"

        Arguments:
            message (str): Message to display

        """

        # TODO(marcus): Implement this.
        self.info(message)

    def heads_up(self, title, message, command=None):
        """Provide a front-and-center message with optional command

        Arguments:
            title (str): Bold and short message
            message (str): Extended message
            command (optional, callable): Function is provided as a button

        """

        # TODO(marcus): Implement this.
        self.info(message)

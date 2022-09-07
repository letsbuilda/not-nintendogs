from nurses_2.app import App
from nurses_2.widgets.button import Button
from nurses_2.widgets.menu import Menu

from not_nintendogs.sprites import AnimSprite, SpriteInfo


class SpriteApp(App):
    async def on_start(self):
        # graphic = GraphicWidget(size_hint=(1.0, 1.0))
        graphic = AnimSprite("Retriever01.png", SpriteInfo.DOG, pos=(4, 3))
        self.add_widget(graphic)

        # Setup menu
        menu_dict = {
            ("Actions", "Ctrl+A"): {
                ("Lie Down", ""): graphic.play_liedown,
                ("Sit", ""): lambda: None,
            },
        }

        self.add_widgets(Menu.from_dict_of_dicts(menu_dict, pos=(2, 0)))

        root_menu = self.children[-1]
        root_menu.is_enabled = False
        # root_menu.children[1].item_disabled = True

        def toggle_root_menu():
            if root_menu.is_enabled:
                root_menu.close_menu()
            else:
                root_menu.open_menu()

        self.add_widget(
            Button(label="Menu", callback=toggle_root_menu, pos=(1, 0), size=(1, 6))
        )

        graphic.start_animation()

        # await asyncio.sleep(2)
        # graphic.play_liedown()


SpriteApp(title="Sprite Test").run()

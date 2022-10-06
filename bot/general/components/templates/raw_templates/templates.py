import os

from dataclasses import dataclass

from .structure import RawTemplate


ROOT_PATH = os.path.abspath(os.path.dirname(__file__))


@dataclass
class Paths:

    @dataclass
    class FisherBotTemplates:

        __fisher_bot_templates = os.path.join(
            ROOT_PATH, 'fisher_bot'
        )
        bobbers = os.path.join(__fisher_bot_templates, 'bobbers')
        status_bar_components = os.path.join(
            __fisher_bot_templates, 'status_bar_components'
        )
        assert os.path.exists(status_bar_components) is True
        other = os.path.join(__fisher_bot_templates, 'other')


@dataclass
class RawTemplates:

    @dataclass
    class FisherBotRawTemplates:
        bobbers = (
            RawTemplate(
                label=str(*bobber.split('.')[:-1]),
                path=os.path.join(Paths.FisherBotTemplates.bobbers, bobber)
            )
            for bobber in os.listdir(Paths.FisherBotTemplates.bobbers)
            if os.path.isfile(os.path.join(Paths.FisherBotTemplates.bobbers, bobber))
        )
        status_bar_components = (
            RawTemplate(
                label=str(*status_bar_component.split('.')[:-1]),
                path=os.path.join(
                    Paths.FisherBotTemplates.status_bar_components, status_bar_component
                )
            )
            for status_bar_component in os.listdir(Paths.FisherBotTemplates.status_bar_components)
            if os.path.isfile(os.path.join(Paths.FisherBotTemplates.status_bar_components, status_bar_component))
        )
        other = (
            RawTemplate(
                label=str(*other.split('.')[:-1]),
                path=os.path.join(Paths.FisherBotTemplates.other, other)
            )
            for other in os.listdir(Paths.FisherBotTemplates.other)
            if os.path.isfile(os.path.join(Paths.FisherBotTemplates.other, other))
        )

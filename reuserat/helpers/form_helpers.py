from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, HTML, Field


class CrispyMaterialForm(forms.Form):
    material_icons = {}

    def __init__(self, *args, **kwargs):
        super(CrispyMaterialForm, self).__init__(*args, **kwargs)

        if not hasattr(self, 'helper'):
            self.helper = FormHelper()

        if not self.helper.layout:
            self.helper.layout = Layout()


        for field in self.fields:
            if self.material_icons:
                self.helper.layout.append(
                    Div(
                        HTML(
                            """
                                <span class="input-group-addon">
                                    <i class="material-icons">{icon}</i>
                                </span>
                            """.format(icon=self.material_icons.get(field))),
                        field,
                        css_class="input-group")

                )


        self.helper.form_tag = False
        self.helper.label_class = 'control-label'

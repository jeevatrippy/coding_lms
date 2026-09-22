import frappe
from frappe.model.document import Document

class LabSubmission(Document):
    def before_save(self):
        # Auto-compute final total score: Pre-Lab Final + In-Lab Final + Viva
        self.final_total_score = (
            float(self.pre_lab_final_score or self.pre_lab_auto_score or 0) +
            float(self.in_lab_final_score or self.in_lab_auto_score or 0) +
            float(self.viva_score or 0)
        )

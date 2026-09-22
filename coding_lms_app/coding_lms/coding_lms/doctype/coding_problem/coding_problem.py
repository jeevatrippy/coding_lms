import frappe
from frappe.model.document import Document

class CodingProblem(Document):
    def validate(self):
        # Calculate overall weightage
        if self.testcases:
            total = sum(float(tc.weightage or 0) for tc in self.testcases)

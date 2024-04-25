from odoo.tests.common import TransactionCase, new_test_user


class CrmNACECase(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.uid = new_test_user(
            cls.env,
            login="user",
            groups="base.group_user,sales_team.group_sale_salesman",
        )

        partner_industry = cls.env["res.partner.industry"]
        cls.nace_0 = partner_industry.create(
            {"name": "name_0", "full_name": "code_0 - name_0"}
        )
        cls.nace_1 = partner_industry.create(
            {"name": "name_1", "full_name": "code_1 - name_1"}
        )
        cls.nace_2 = partner_industry.create(
            {"name": "name_2", "full_name": "code_2 - name_2"}
        )

    def test_data_transferred_to_partner(self):
        """Data is moved to partner when creating it from lead."""
        # Create a lead with nace codes but without partner yet
        lead = self.env["crm.lead"].create(
            {
                "name": "test lead",
                "partner_name": "someone",
                "industry_id": self.nace_0.id,
                "secondary_industry_ids": [(4, self.nace_1.id), (4, self.nace_2.id)],
            }
        )
        self.assertFalse(lead.partner_id)
        # Create that partner automatically
        partner = lead._create_customer()
        self.assertEqual(partner.industry_id, self.nace_0)
        self.assertEqual(partner.secondary_industry_ids, self.nace_1 | self.nace_2)

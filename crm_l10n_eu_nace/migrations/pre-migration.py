import logging

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    # get all used old naces in leads
    cr.execute(
        """
    SELECT nace.id, nace.code, nace.name
    FROM res_partner_nace nace
    WHERE nace.id in (
            SELECT DISTINCT lead.nace_id
            FROM crm_lead lead
            WHERE lead.nace_id IS NOT null
        )
    """
    )
    nace_ids = cr.fetchall()
    # get all industries
    cr.execute("SELECT id, full_name FROM res_partner_industry")
    industry_ids = cr.fetchall()
    # industry dict with codes
    industry_dict = {
        industry["full_name"].split(" - ")[0]: industry["id"]
        for industry in industry_ids
    }
    # nace as dict
    nace_dict = {
        nace["id"]: {"code": nace["code"], "name": nace["name"]} for nace in nace_ids
    }
    # map nace with new industry model
    for nace_id, nace_data in nace_dict.items():
        code = nace_data.get("code", "")
        industry_id = industry_dict.get(code, False)
        nace_dict[nace_id].update({"industry_id": industry_id})
    # update all leads industry_id from the old nace_id : m2o relation
    for nace_id, nace_data in nace_dict.items():
        industry_id = nace_data.get("industry_id", False)
        if industry_id:
            cr.execute(
                "UPDATE crm_lead SET industry_id = %s WHERE nace_id = %s",
                (industry_id, nace_id),
            )
    # update old new_industry_id from leads : m2m relation
    # 3rd from table
    cr.execute(
        "SELECT crm_lead_id, res_partner_nace_id FROM crm_lead_res_partner_nace_rel"
    )
    crm_lead_nace_rel = cr.fetchall()
    for lead_id, nace_id in crm_lead_nace_rel:
        industry_id = nace_dict[nace_id].get("industry_id", False)
        if industry_id:
            cr.execute(
                "INSERT INTO crm_lead_res_partner_industry_rel "
                "(crm_lead_id, res_partner_industry_id) "
                "VALUES (%s, %s)",
                (lead_id, industry_id),
            )

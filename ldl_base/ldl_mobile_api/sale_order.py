# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from itertools import groupby
from datetime import datetime, timedelta
from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools import float_is_zero, float_compare, DEFAULT_SERVER_DATETIME_FORMAT
from odoo.tools.misc import formatLang
import odoo.addons.decimal_precision as dp
from dateutil.relativedelta import relativedelta


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.model
    def _get_report_sale(self,from_date,to_date,type_date):
        date_from = datetime.fromtimestamp(from_date) + timedelta(hours=7)
        date_to = datetime.fromtimestamp(to_date) + timedelta(hours=7)
        query = """SELECT s.amount_total,s.date_order,s.amount_untaxed,s.name
                    FROM sale_order s
                    WHERE state in ('sale','done') and (s.date_order>=%s and s.date_order<=%s)
                    ORDER BY date_order;"""

        self.env.cr.execute(query, (str(date_from), str(date_to)))
        sale_order = self.env.cr.dictfetchall()
        ls_sale = {}
        if type_date == 'day':
            for n in range(int ((date_to  - date_from).days)):
                date_next =  (date_from + timedelta(n)).strftime("%Y-%m-%d")
                result = filter(lambda s: str(datetime.strptime(s['date_order'],'%Y-%m-%d %H:%M:%S').date()) == date_next,sale_order )
                if result:
                    ls_sale[str(date_next)] = result

        elif type_date == 'month':
            month_year_from = int('%s%s'%(date_from.month,date_from.year))
            month_year_to = int('%s%s'%(date_to.month,date_to.year))
            while month_year_from <= month_year_to:
                month_from = date_from.month
                year_from = date_from.year
                result = filter(lambda s: datetime.strptime(s['date_order'],'%Y-%m-%d %H:%M:%S').month == month_from and datetime.strptime(s['date_order'],'%Y-%m-%d %H:%M:%S').year == year_from,sale_order )
                date_from += relativedelta(months=1)
                month_year_from = int('%s%s'%(date_from.month,date_from.year))
                if result:
                    month_year = '%s-%s'%(month_from,year_from)
                    ls_sale[month_year] = result
        elif type_date == 'year':
            year_from = date_from.year
            year_to = date_from.year
            while year_from <= year_to:
                result = filter(lambda s: datetime.strptime(s['date_order'],'%Y-%m-%d %H:%M:%S').year == year_from,sale_order )
                if result:
                    ls_sale[year_from] = result
                year_from += 1
        return ls_sale
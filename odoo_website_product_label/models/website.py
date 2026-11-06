# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api
from odoo import SUPERUSER_ID

class product_template(models.Model):
	_inherit = 'product.template'
	
	label_type = fields.Selection([('custom','Custom Ribbons'),('defined','Pre-defined Labels')])
	lbl_title = fields.Text('Label Title')
	select_label = fields.Many2one('website.product.label','Select Product Label')
	label_image = fields.Binary('Label Image')

	@api.onchange('select_label')
	def onchange_product_label(self):
		self.label_image = self.select_label.image        
			
			
class website_product_label(models.Model):
	_name='website.product.label'
	_description="Website Producr Label"

	name  =  fields.Char('Label Name')
	image = fields.Binary('Image')
	label_type = fields.Selection([('custom','Custom Ribbons'),('defined','Pre-defined Labels')])
	height = fields.Char('Height (in px)')
	width = fields.Char('Width (in px)')
	position = fields.Selection([
		('topleft', 'Top Left'),
		('topright', 'Top Right'),
		('topcenter', 'Top Center'),
		('center', 'Center'),
		('bottomleft', 'Bottom Left'),
		('bottomright', 'Bottom Right'),
		('bottomcenter', 'Bottom Center'),
		], 'Position of Label', default="topleft")
	margin_top = fields.Char('Margin Top (in px)')
	margin_bottom = fields.Char('Margin Bottom (in px)')
	margin_left = fields.Char('Margin Left (in px)')
	margin_right = fields.Char('Margin Right (in px)')
	rotate_label = fields.Selection([('rt_left','Rotate Left'),('rt_right','Rotate Right')],'Rotate Label')
	rotate_value = fields.Char('Rotation Value (in deg)')

	font_color = fields.Char('Font Color')
	font_size = fields.Char('Font Size (in px)')
	font_top = fields.Char('Top (in px)')
	font_bottom = fields.Char('Bottom (in px)')
	font_left = fields.Char('Left (in px)')
	font_right = fields.Char('Right (in px)')
	font_rotate_label = fields.Selection([('rt_left','Font Rotate Left'),('rt_right','Font Rotate Right')],'Rotate Fonts')
	font_rotate_value = fields.Char('Font Rotation Value (in deg)')

	def unset_font_rotation(self):
		self.font_rotate_label = False

	def unset_img_rotation(self):
		self.rotate_label = False     
		
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:    

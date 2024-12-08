# -*- coding: utf-8 -*-
from docutils.nodes import title
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import logging
import secrets
import re

from pygments.lexer import default

_logger = logging.getLogger(__name__)


class Student(models.Model):
    _name = 'school.student'
    _description = 'Student Record'

    name = fields.Char(
        string="Nom",
        required=True,
        help='Nombre del estudiante')

    dni = fields.Char(
        string="dni",
        readonly=False,
        required=True,
        help='dni')

    birth_year = fields.Integer(
        string="Año de nacimiento"
    )
    description = fields.Text(
        string="Descripción"
    )

    # @api.depends('name') esto era cuando iba despues de la creacion de passw
    #    def _get_password(self):
    #           print('\033[94m', self, '\033[0m')  # Esto es para ponerle colores al print
    #          password = secrets.token_urlsafe(7)
    #         _logger.debug('\033[94m'+ str(password)+ '\033[0m')  # Lo mismo que el print pero en el logger
    #        return password
    # raise Warning(_('Errorrr'))  # Aviso de errores (comentado)

    password = fields.Char(
        default=lambda s: secrets.token_urlsafe(7)

    )
    is_student =fields.Boolean()
    enrollment_date = fields.Datetime(
        default=lambda self: fields.Datetime.now()
    )
    last_login = fields.Datetime(

    )
    photo = fields.Image(
        max_width=200,
        max_height=200
    )
    classroom = fields.Many2one(
        'school.classroom',
        domain="[('level','=', level)]",
        ondelete='set null',
        string="Clase actual",
        help='Clase asignada'
    )
    classroom_last_year = fields.Many2one(
        'school.classroom',
        ondelete='set null',
        string="Clase anterior",
        help='Clase del año pasado'
    )
    teachers = fields.Many2many(
        'school.teacher',
        related='classroom.teachers',
        readonly=True,
        string="Profesores"
    )
    level= fields.Selection([('1','1'),('2','2')])
    state=fields.Selection([('1','Enrolled'),('2', 'Student'), ('3','Ex-Student')], default='1')

    @api.constrains('dni')
    def _check_dni(self):
        regex = re.compile(r'[0-9]{8}[a-z]\Z', re.I)
        for s in self:
            if regex.match(s.dni):
                _logger.info('El dni match')
            else:
                raise ValidationError('DNI INVALIDO')

    _sql_constraints = [('dni_uniq', 'unique(dni)', 'DNI EXIST')]

    def regenerate_password(self):
        for s in self:
            password = secrets.token_urlsafe(7)
            s.write({'password': password})

    @api.onchange('birth_year')
    def _onchange_byear(self):
            if self.birth_year > 2010:
                self.birth_year = 2000
                return {'warning':
                            {'title':'Bad birth year',
                             'message': 'The student is too young',
                             'type':'notification'}
                }
    @api.onchange('level')
    def _onchange_level(self):
        return {
            'domain': {'classroom' : [('level', '=', self.level)]},
        }

class Classroom(models.Model):
    _name = 'school.classroom'
    _description = 'Les clases'

    name = fields.Char()
    level=fields.Selection([('1','1'),('2','2')])

    students = fields.One2many(string='Students', comodel_name='school.student', inverse_name='classroom')
    teachers = fields.Many2many(
        'school.teacher',
        'teachers_classroom',  # Nombre de la tabla intermedia
        'classroom_id',         # Columna que referencia a `school.classroom`
        'teacher_id',           # Columna que referencia a `school.teacher`
        string="Profesores"
    )
    teacher_ly = fields.Many2many(
        'school.teacher',
        'teachers_classroom_ly',  # Nombre de la tabla intermedia para el año anterior
        'classroom_id',            # Columna que referencia a `school.classroom`
        'teacher_id',              # Columna que referencia a `school.teacher`
        string="Profesores año pasado"
    )
    delegate = fields.Many2one('school.student', compute='_get_delegate')
    all_teachers = fields.Many2many('school.teacher', compute='_get_teachers')

    def _get_teachers(self):
        for c in self:
            c.all_teachers = c.teachers + c.teacher_ly

    def _get_delegate(self):
        for c in self:
            c.delegate = c.students[0].id

class Teacher(models.Model):
    _name = 'school.teacher'
    _description = 'Los profes'
    topic = fields.Char()
    phone= fields.Char()
    name = fields.Char()
    classrooms = fields.Many2many(
        'school.classroom',
        'teachers_classroom',  # Nombre de la tabla intermedia
        'teacher_id',           # Columna que referencia a `school.teacher`
        'classroom_id',         # Columna que referencia a `school.classroom`
        string="Clases"
    )
    classrooms_ly = fields.Many2many(
        'school.classroom',
        'teachers_classroom_ly',  # Nombre de la tabla intermedia para el año anterior
        'teacher_id',              # Columna que referencia a `school.teacher`
        'classroom_id',            # Columna que referencia a `school.classroom`
        string="Clases del año pasado"
    )

class seminar(models.Model):
    _name='school.seminar'
    _description = "Descripción del Seminario"

    name=fields.Char()
    date = fields.Datetime()
    finish=fields.Datetime()
    hour=fields.Integer()
    classroom= fields.Many2one('school.classroom')

#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100


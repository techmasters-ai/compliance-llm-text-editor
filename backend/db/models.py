# backend/db/models.py
from sqlalchemy import Column, Integer, String, Text, ForeignKey, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class ComplianceRule(Base):
    __tablename__ = 'compliance_rules'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    description = Column(Text)

class Document(Base):
    __tablename__ = 'documents'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    content = Column(Text)

class Paragraph(Base):
    __tablename__ = 'paragraphs'
    id = Column(Integer, primary_key=True)
    document_id = Column(Integer, ForeignKey('documents.id'))
    content = Column(Text)
    violations = relationship("Violation", back_populates="paragraph")

class Violation(Base):
    __tablename__ = 'violations'
    id = Column(Integer, primary_key=True)
    paragraph_id = Column(Integer, ForeignKey('paragraphs.id'))
    rule_id = Column(Integer, ForeignKey('compliance_rules.id'))
    highlighted_text = Column(Text)
    suggested_fix = Column(Text)
    accepted = Column(Boolean, default=False)

    paragraph = relationship("Paragraph", back_populates="violations")

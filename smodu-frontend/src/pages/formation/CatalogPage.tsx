import { BookOutlined, LockOutlined } from '@ant-design/icons';
import { Card, Col, Empty, Progress, Row, Select, Skeleton, Tag, Typography } from 'antd';
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useCatalog } from '@/hooks/useFormation';
import type { Level } from '@/types';

const { Title, Text } = Typography;

const levelColor: Record<Level, string> = {
  DISCOVERY: 'default',
  BEGINNER: 'blue',
  INTERMEDIATE: 'orange',
  AUTONOMOUS: 'purple',
  PROJECT_READY: 'green',
};

const levelLabel: Record<Level, string> = {
  DISCOVERY: 'Découverte',
  BEGINNER: 'Débutant',
  INTERMEDIATE: 'Intermédiaire',
  AUTONOMOUS: 'Autonome',
  PROJECT_READY: 'Prêt Projet',
};

const CatalogPage = () => {
  const { data: modules, isLoading } = useCatalog();
  const navigate = useNavigate();
  const [filterLevel, setFilterLevel] = useState<Level | 'ALL'>('ALL');

  const filtered = modules?.filter(m =>
    filterLevel === 'ALL' ? true : m.level === filterLevel
  );

  if (isLoading) return <Skeleton active paragraph={{ rows: 6 }} />;

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 24 }}>
        <Title level={2} style={{ margin: 0 }}>Catalogue de Formation</Title>
        <Select
          value={filterLevel}
          onChange={setFilterLevel}
          style={{ width: 180 }}
          options={[
            { value: 'ALL', label: 'Tous les niveaux' },
            ...Object.entries(levelLabel).map(([v, l]) => ({ value: v, label: l })),
          ]}
        />
      </div>

      {!filtered?.length ? (
        <Empty description="Aucun module disponible" />
      ) : (
        <Row gutter={[16, 16]}>
          {filtered.map(module => (
            <Col xs={24} sm={12} lg={8} key={module.id}>
              <Card
                hoverable={!module.is_locked}
                style={{
                  opacity: module.is_locked ? 0.6 : 1,
                  cursor: module.is_locked ? 'not-allowed' : 'pointer',
                  height: '100%',
                }}
                onClick={() => !module.is_locked && navigate(`/formation/modules/${module.id}`)}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 8 }}>
                  <Tag color={levelColor[module.level]}>{levelLabel[module.level]}</Tag>
                  {module.is_locked && <LockOutlined style={{ color: '#7a7974' }} />}
                </div>
                <Title level={5} style={{ margin: '8px 0' }}>{module.title}</Title>
                <Text type="secondary" style={{ fontSize: 13 }}>{module.description}</Text>
                <div style={{ marginTop: 16 }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 4 }}>
                    <Text style={{ fontSize: 12 }} type="secondary">Progression</Text>
                    <Text style={{ fontSize: 12 }}>{module.completion_percentage}%</Text>
                  </div>
                  <Progress
                    percent={module.completion_percentage}
                    showInfo={false}
                    strokeColor="#01696f"
                    size="small"
                  />
                </div>
                <div style={{ marginTop: 12 }}>
                  <Text type="secondary" style={{ fontSize: 12 }}>
                    <BookOutlined style={{ marginRight: 4 }} />
                    {module.lessons?.length ?? 0} leçons
                  </Text>
                </div>
              </Card>
            </Col>
          ))}
        </Row>
      )}
    </div>
  );
};

export default CatalogPage;

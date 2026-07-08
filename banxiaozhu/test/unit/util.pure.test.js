const util = require('../../utils/util.js');

describe('util pure helpers', () => {
  test('uuidtostr removes hyphens', () => {
    expect(util.uuidtostr('a1b2c3d4-e5f6-7890-abcd-ef1234567890')).toBe(
      'a1b2c3d4e5f67890abcdef1234567890'
    );
  });

  test('strtouuid inserts hyphens', () => {
    expect(util.strtouuid('a1b2c3d4e5f67890abcdef1234567890')).toBe(
      'a1b2c3d4-e5f6-7890-abcd-ef1234567890'
    );
  });

  test('strtodate formats YYYYMMDD', () => {
    expect(util.strtodate('20240115')).toBe('2024-01-15');
  });

  test('getToday returns YYYY-MM-DD string', () => {
    const today = util.getToday();
    expect(today).toMatch(/^\d{4}-\d{2}-\d{2}$/);
  });

  test('dateDelta shifts days from ISO date string', () => {
    const base = '2024-01-15';
    expect(util.dateDelta(base, -1)).toBe('2024-01-14');
    expect(util.dateDelta(base, 1)).toBe('2024-01-16');
  });
});

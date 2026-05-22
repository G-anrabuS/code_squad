import 'package:flutter_test/flutter_test.dart';

import 'package:flutter_frontend/main.dart';

void main() {
  testWidgets('app boots', (WidgetTester tester) async {
    await tester.pumpWidget(const CodeSquadApp());

    expect(find.text('Code Squad'), findsOneWidget);
  });
}

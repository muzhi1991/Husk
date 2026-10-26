import 'package:flutter/widgets.dart';

void main() => runApp(const Probe());
class Probe extends StatefulWidget {
  const Probe({super.key});
  @override
  State<Probe> createState() => _ProbeState();
}
class _ProbeState extends State<Probe> {
  int count = 0;
  bool details = false;
  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      debugPrint('HUSK_PROBE:first-frame');
    });
  }
  Widget button(String label, VoidCallback action) => GestureDetector(
    onTap: action,
    child: Container(
      margin: const EdgeInsets.symmetric(vertical: 12),
      padding: const EdgeInsets.all(20),
      color: const Color(0xff2255aa),
      child: Text(label, style: const TextStyle(color: Color(0xffffffff), fontSize: 24)),
    ),
  );
  @override
  Widget build(BuildContext context) => Directionality(
    textDirection: TextDirection.ltr,
    child: ColoredBox(
      color: const Color(0xffeeeeee),
      child: DefaultTextStyle(
        style: const TextStyle(color: Color(0xff111111), fontSize: 24),
        child: Padding(
          padding: const EdgeInsets.fromLTRB(24, 100, 24, 40),
          child: Column(crossAxisAlignment: CrossAxisAlignment.stretch, children: [
            const Text('Flutter compatibility probe'),
            const SizedBox(height: 24),
            const Text('Latin: ABC xyz 0123456789'),
            const Text('中文字体测试'),
            const SizedBox(height: 24),
            Text(details ? 'Second page / 第二页' : 'Home / 首页'),
            Text('Count: $count'),
            button('Increment / 加一', () {
              setState(() => count++);
              debugPrint('HUSK_PROBE:count=$count');
            }),
            button(details ? 'Back / 返回' : 'Next / 下一页', () {
              setState(() => details = !details);
              debugPrint('HUSK_PROBE:page=${details ? "second" : "home"}');
            }),
          ]),
        ),
      ),
    ),
  );
}
